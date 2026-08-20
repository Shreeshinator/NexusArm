"""camera_bridge — pull MJPEG camera streams over WiFi and republish as ROS.

The ESP32-CAM and phone apps like "DroidCam" or "IP Webcam" all serve video as
MJPEG: an endless HTTP response containing one JPEG image after another, each
separated by a `boundary` string.  This node connects to those URLs, slices each
JPEG out of the stream, and republishes it on a ROS topic as
sensor_msgs/CompressedImage (the JPEG bytes are forwarded untouched — no
decode/re-encode, so almost no CPU).

Design choices (keep these in mind if you edit):
  * PASSTHROUGH, NOT DECODE — we never call cv2 here. The LeRobot recorder is
    the only thing that must decode, and it does that itself.  Decoding here
    would just waste CPU and add latency.
  * ONLY NEW FRAMES — the timer is a *cap* (max publish rate), not a clock.
    A frame is published only if it differs from the last one, so a slow camera
    never produces duplicate frames in the dataset.
  * depth=1 KEEP_LAST — the recorder only ever wants the newest frame; stale
    frames are useless for training and just waste memory.

Cameras:
  * ESP32-CAM  -> http://<esp32-ip>:81/stream        (cameraWebServer example)
  * DroidCam   -> http://<phone-ip>:<port>/video     (DroidCam; port shown in
                                                    the phone app, default 4747)
  * IP Webcam  -> http://<phone-ip>:8080/video       (Android "IP Webcam" app)

Run (URLs as params; leave a URL empty to disable that camera):
    ros2 run robot_arm_hardware camera_bridge --ros-args \
        -p gripper_url:=http://192.168.1.50:81/stream \
        -p front_url:=http://192.168.1.51:4747/video \
        -p fps:=15.0
"""
import threading
import time
import urllib.request

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage


class CameraBridge(Node):
    def __init__(self):
        super().__init__("camera_bridge")

        self.declare_parameter("gripper_url", "")
        self.declare_parameter("front_url", "")
        self.declare_parameter("gripper_topic", "/gripper_cam/image_raw/compressed")
        self.declare_parameter("front_topic", "/front_cam/image_raw/compressed")
        self.declare_parameter("fps", 15.0)

        self._gripper_url = self.get_parameter("gripper_url").get_parameter_value().string_value
        self._front_url = self.get_parameter("front_url").get_parameter_value().string_value
        fps = self.get_parameter("fps").get_parameter_value().double_value
        gripper_topic = self.get_parameter("gripper_topic").get_parameter_value().string_value
        front_topic = self.get_parameter("front_topic").get_parameter_value().string_value

        # QoS fix 1: publisher MUST be BEST_EFFORT depth=1 to match lerobot_infer
        # subscriber (BEST_EFFORT). DDS RELIABLE<->BEST_EFFORT are incompatible —
        # with default RELIABLE the image never arrives and _tick warns "no front image".
        img_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self._pub_gripper = self.create_publisher(CompressedImage, gripper_topic, img_qos)
        self._pub_front = self.create_publisher(CompressedImage, front_topic, img_qos)

        self._lock = threading.Lock()
        self._latest = {}       # key -> bytes (newest JPEG from that camera)
        self._published = {}    # key -> bytes (last bytes we actually published)
        self._frames = {}       # key -> int (frames parsed from stream)

        # Cap the publish rate; frames are still dropped if unchanged.
        self._timer = self.create_timer(1.0 / max(fps, 1.0), self._publish_latest)
        self._diag = self.create_timer(5.0, self._log_stats)

        # One reader thread per enabled camera.
        self._threads = []
        for key, url in (("gripper", self._gripper_url), ("front", self._front_url)):
            if url:
                t = threading.Thread(target=self._stream, args=(key, url), daemon=True)
                t.start()
                self._threads.append(t)
                self.get_logger().info(f"{key} camera: {url}")

        enabled = len(self._threads)
        self.get_logger().info(
            f"camera_bridge ready: {enabled} camera(s) at up to {fps:.1f} fps "
            f"-> {gripper_topic}, {front_topic}"
        )

    # -- stream reading -----------------------------------------------------
    def _stream(self, key, url):
        """Keep the HTTP stream alive forever, reconnecting on any error."""
        while rclpy.ok():
            try:
                self._read_stream(key, url)
            except Exception as exc:  # noqa: BLE001 — reconnect on any failure
                self.get_logger().warn(f"{key} stream error ({exc}); reconnect in 1s")
                time.sleep(1.0)

    def _read_stream(self, key, url):
        resp = urllib.request.urlopen(url, timeout=10.0)
        ctype = resp.headers.get("Content-Type", "")
        boundary = self._extract_boundary(ctype)
        self.get_logger().info(
            f"{key}: Content-Type={ctype!r} header_boundary={boundary!r}")
        init = b""
        if boundary is None:
            # Not announced in the header (DroidCam sends the boundary only in
            # the body, e.g. "--dcmjpeg"). Sniff it from the first bytes.
            init = resp.read(512)
            boundary = self._sniff_boundary(init)
            self.get_logger().info(
                f"{key}: sniffed boundary={boundary!r} first_bytes={init[:24]!r}")
            if boundary is None:
                # A single JPEG (some endpoints), not a stream.
                self._store(key, init + resp.read())
                return
        self._read_multipart(resp, key, boundary, init)

    @staticmethod
    def _extract_boundary(content_type):
        for part in content_type.split(";"):
            part = part.strip()
            if part.startswith("boundary="):
                b = part[len("boundary="):].strip().strip('"')
                return b[2:] if b.startswith("--") else b
        return None

    @staticmethod
    def _sniff_boundary(data: bytes):
        """Boundary name from a body that starts like '--dcmjpeg\\r\\n'."""
        if data.startswith(b"--"):
            line_end = data.find(b"\r\n")
            if line_end != -1:
                candidate = data[2:line_end].decode("ascii", "ignore").strip()
                if candidate:
                    return candidate
        return None

    def _read_multipart(self, resp, key, boundary, init=b""):
        """Slice JPEG frames out of a multipart/x-mixed-replace response."""
        marker = b"--" + boundary.encode()
        buf = init
        while rclpy.ok():
            chunk = resp.read(4096)
            if not chunk:
                break
            buf += chunk
            while True:
                idx = buf.find(marker)
                if idx == -1:
                    break
                sep = buf.find(b"\r\n\r\n", idx)
                if sep == -1:
                    break
                nxt = buf.find(marker, sep + 4)
                if nxt == -1:
                    break
                jpeg = buf[sep + 4:nxt].rstrip(b"\r\n")
                self._store(key, jpeg)
                buf = buf[nxt:]

    def _store(self, key, data):
        with self._lock:
            self._latest[key] = data
            self._frames[key] = self._frames.get(key, 0) + 1

    def _log_stats(self):
        with self._lock:
            frames = dict(self._frames)
            latest = {k: (len(v) if v is not None else 0)
                      for k, v in self._latest.items()}
            published = {k: (len(v) if v is not None else 0)
                         for k, v in self._published.items()}
        for key in frames:
            self.get_logger().info(
                f"[diag] {key}: parsed={frames[key]} frames | "
                f"latest_size={latest.get(key, 0)}B | "
                f"published_size={published.get(key, 0)}B")
        if not frames:
            self.get_logger().warn("[diag] no frames parsed from any camera yet")

    # -- publishing ---------------------------------------------------------
    def _publish_latest(self):
        for key, pub in (("gripper", self._pub_gripper), ("front", self._pub_front)):
            with self._lock:
                data = self._latest.get(key)
                last = self._published.get(key)
            if data is None or data == last:
                continue  # no frame yet, or nothing new — don't duplicate
            msg = CompressedImage()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.format = "jpeg"
            msg.data = data
            pub.publish(msg)
            with self._lock:
                self._published[key] = data


def main(args=None):
    rclpy.init(args=args)
    node = CameraBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
