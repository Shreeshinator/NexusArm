#!/usr/bin/env python3
"""Offline verification for ACT policy (step 3).

Loads shreeshinator/arm-pick-blocks-act-first + shreeshinator/arm-picking-blocks-real,
runs inference on N random frames and on a sequential episode, and logs
pred vs ground-truth distances. No ROS or hardware required.

Usage:
  .venv/bin/python scripts/verify_act.py --hf-repo shreeshinator/arm-pick-blocks-act-first --dataset-repo shreeshinator/arm-picking-blocks-real

This mirrors the preprocessing in lerobot_infer.py (dataset already decoded to float [0,1]).
"""
import argparse
import random
import numpy as np
import torch
from lerobot.policies.act.configuration_act import ACTConfig
from lerobot.policies.factory import make_policy
from lerobot.datasets.lerobot_dataset import LeRobotDataset, LeRobotDatasetMetadata


def load_policy(hf_repo, dataset_repo, device):
    cfg = ACTConfig.from_pretrained(hf_repo)
    cfg.pretrained_path = hf_repo
    cfg.device = device
    meta = LeRobotDatasetMetadata(dataset_repo)
    policy = make_policy(cfg, ds_meta=meta)
    policy.eval()
    try:
        policy.to(device)
    except Exception:
        pass
    return policy, cfg


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hf-repo", default="shreeshinator/arm-pick-blocks-act-first")
    p.add_argument("--dataset-repo", default="shreeshinator/arm-picking-blocks-real")
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--samples", type=int, default=10)
    args = p.parse_args()

    device = args.device
    print(f"loading policy {args.hf_repo} on {device} ...")
    policy, cfg = load_policy(args.hf_repo, args.dataset_repo, device)
    print(f"  chunk_size={cfg.chunk_size} n_action_steps={cfg.n_action_steps}")
    ds = LeRobotDataset(args.dataset_repo)
    print(f"dataset {args.dataset_repo}: len={len(ds)} fps={ds.fps}")

    # random frames
    print("\n=== Random frames (reset each time, compare pred vs gt for same timestep) ===")
    random.seed(0)
    indices = random.sample(range(len(ds)), min(args.samples, len(ds)))
    errs = []
    for idx in indices:
        f = ds[idx]
        batch = {
            "observation.state": f["observation.state"].unsqueeze(0).to(device),
            "observation.images.front": f["observation.images.front"].unsqueeze(0).to(device),
            "task": [f["task"]],
        }
        policy.reset()
        with torch.no_grad():
            pred = policy.select_action(batch)
        pred_np = pred[0].cpu().numpy()
        gt = f["action"].numpy()
        cur = f["observation.state"].numpy()
        err = float(np.linalg.norm(pred_np - gt))
        errs.append(err)
        print(f" idx {idx:5d} ep {int(f['episode_index']):2d} fr {int(f['frame_index']):3d} "
              f"pred {np.round(pred_np,2).tolist()} gt {np.round(gt,2).tolist()} err {err:.3f} "
              f"pred-state {np.linalg.norm(pred_np-cur):.3f}")
    print(f"mean random err {np.mean(errs):.3f} max {np.max(errs):.3f}")

    # sequential episode (queue consumption)
    ep = int(ds[0]["episode_index"])
    # pick episode with most frames for stable test
    from collections import Counter
    eps = [int(ds[i]["episode_index"]) for i in range(len(ds))]
    ep = Counter(eps).most_common(1)[0][0]
    indices_ep = [i for i in range(len(ds)) if int(ds[i]["episode_index"]) == ep]
    print(f"\n=== Sequential episode {ep} ({len(indices_ep)} frames), streaming via select_action queue ===")
    policy.reset()
    seq_errs = []
    for k, idx in enumerate(indices_ep[:30]):
        f = ds[idx]
        batch = {
            "observation.state": f["observation.state"].unsqueeze(0).to(device),
            "observation.images.front": f["observation.images.front"].unsqueeze(0).to(device),
            "task": [f["task"]],
        }
        with torch.no_grad():
            pred = policy.select_action(batch)
        pred_np = pred[0].cpu().numpy()
        gt = f["action"].numpy()
        err = float(np.linalg.norm(pred_np - gt))
        seq_errs.append(err)
        print(f"  fr {k:2d} pred {np.round(pred_np,2).tolist()} gt {np.round(gt,2).tolist()} err {err:.3f}")
    print(f"mean seq err (first 30) {np.mean(seq_errs):.3f} max {np.max(seq_errs):.3f}")

    # chunk mode
    print(f"\n=== Chunk prediction from first frame of episode {ep} ===")
    policy.reset()
    f0 = ds[indices_ep[0]]
    batch0 = {
        "observation.state": f0["observation.state"].unsqueeze(0).to(device),
        "observation.images.front": f0["observation.images.front"].unsqueeze(0).to(device),
        "task": [f0["task"]],
    }
    with torch.no_grad():
        chunk = policy.predict_action_chunk(batch0)
    chunk_np = chunk[0].cpu().numpy()
    print(f"chunk shape {chunk.shape} (1, chunk_size, 5)")
    for i in range(min(5, len(indices_ep))):
        gt_i = ds[indices_ep[i]]["action"].numpy()
        print(f"  chunk[{i}] {np.round(chunk_np[i],2).tolist()} vs gt[t+{i}] {np.round(gt_i,2).tolist()} err {np.linalg.norm(chunk_np[i]-gt_i):.3f}")

    print("\nDone. If mean err >> 0.3 rad (~17 deg), the model may be underfit or dataset action==state. "
          "Check training: dataset fps is 15, image 480x640, action=5 joints.")


if __name__ == "__main__":
    main()
