> **📖 Docs roadmap:** not sure what to read next? See the [Documentation Roadmap](README.md) — it gives the exact reading order for your goal.

# Custom Training — Train ACT on Your Demos (Free: Colab / Kaggle)

> You collected 50–100 clean episodes with `05_DATA_COLLECTION.md` — now turn them into a policy that runs on the real arm via `06_INFERENCE.md`. No paid GPU needed: Colab (T4, ~12 h free) or Kaggle (P100/T4×2, 30 h/week free) is enough for ACT.

This doc is concrete and end-user focused — copy-paste friendly.

---

## 1. What you'll train

* **Policy:** `ACT` (Action Chunking Transformer) — same as `shreeshinator/arm-pick-blocks-act-first` (chunk 100, trained on 480×640 front cam, 5 joints).
* **Dataset:** your `your-hf-username/your-dataset` from `05_DATA_COLLECTION.md` (v3, images + `observation.state` + `action`).
* **Output:** a Hugging Face repo `your-hf-username/your-policy` you can pass to `lerobot_infer.py` as `hf_repo` (see `06_INFERENCE.md` §2).

---

## 2. One-time setup (Colab / Kaggle notebook)

Create a **new notebook** (Colab: `Runtime → Change runtime type → T4 GPU`, Kaggle: `Settings → Accelerator → GPU P100`).

```python
# Cell 1 — install exact pins (matches 01_SETUP.md §4 — don't drift!)
!pip install "setuptools==79.*" -q
!pip install "lerobot==0.6.1" "numpy==1.26.4" "opencv-python-headless" h5py datasets -q
!pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 -q  # Colab/Kaggle have CUDA 12.1
!pip list | grep -E "lerobot|torch|numpy"

# Cell 2 — log in to Hugging Face (needed to read your private dataset + push checkpoints)
# Create a token at https://huggingface.co/settings/tokens (write access), then:
from huggingface_hub import login
login()  # paste token when prompted

# Or non-interactive: !huggingface-cli login --token $HF_TOKEN
```

> **Colab tip:** `Runtime → Change runtime type → T4` is free. If it says “no GPU”, wait or try Kaggle — Kaggle P100 has more free hours/week.

---

## 3. Train — one command (free, ~2–6 h)

Adapt the ACT preset for our arm. The key args mirror the dataset's `fps` and `chunk_size`.

```bash
# In notebook terminal (! prefix) or SSH. Replace repo-ids:
!lerobot-train \
  --dataset.repo_id=your-hf-username/your-dataset \
  --policy.type=act \
  --policy.chunk_size=100 \
  --policy.n_action_steps=100 \
  --dataset.fps=15 \
  --batch_size=8 \
  --steps=50000 \
  --save_freq=5000 \
  --save_checkpoint=true \
  --output_dir=outputs/train/act_arm_pick \
  --job_name=act_arm_pick \
  --wandb.enable=false
```

What this does:
* Loads your dataset from the Hub (cached to `~/.cache/huggingface/lerobot` on the VM).
* Uses the **policy training preset** (`use_policy_training_preset=true` by default) — sensible `lr`, `weight_decay`, `optimizer` for ACT.
* Saves checkpoints every `5000` steps to `outputs/train/act_arm_pick/checkpoints/` + final model to `outputs/train/act_arm_pick/pretrained_model/`.
* On Hub push, the `normalizer` stats (`policy_preprocessor_step_3_normalizer_processor.safetensors` with visual `mean 0.485/0.456/0.406` etc.) are saved automatically — `lerobot_infer.py` needs them (see `06_INFERENCE.md` §6).

**Tune if needed:**
* Small dataset (30 eps) → lower `--steps 20000`, `--batch_size 4`.
* GPU OOM → `--batch_size 4` or `--batch_size 2`, keep `--steps` same.
* Want faster iterate → `--save_freq 2000`.

Check logs: `outputs/train/act_arm_pick/` has `train_config.json` + `checkpoints/`.

---

## 4. Push to Hub (so the arm can pull it)

```bash
# Push final model (or every checkpoint with --save_checkpoint_to_hub true)
!huggingface-cli upload your-hf-username/your-policy outputs/train/act_arm_pick/pretrained_model --repo-type model

# Or let training push automatically:
# add --policy.repo_id=your-hf-username/your-policy to the lerobot-train command above
# + it will push checkpoints as they are written.
```

Verify at `https://huggingface.co/your-hf-username/your-policy` — you should see `config.json`, `model.safetensors`, and `policy_preprocessor_step_3_normalizer_processor.safetensors`.

Then deploy as in `06_INFERENCE.md` §2–3, just change `hf_repo` + `dataset_repo`:

```bash
.venv/bin/python -m robot_arm_hardware.lerobot_infer --ros-args \
  -p hf_repo:=your-hf-username/your-policy \
  -p dataset_repo:=your-hf-username/your-dataset \
  -p task:="place the block in the bowl" -p fps:=15.0 -p n_action_steps:=50
```

---

## 5. Resume — the friendly part (Colab/Kaggle pre-emption, or you stopped early)

Both **local** and **Hub** checkpoints resume cleanly with `--resume`.

### A. Resume from a local checkpoint (still on same VM)

You were at step 20000, Colab timed out — outputs are still on disk:

```bash
!lerobot-train \
  --config_path=outputs/train/act_arm_pick/checkpoints/20000/pretrained_model/train_config.json \
  --resume=true
# CLI flags still override: e.g. add --steps=80000 to extend training
```

Notes:
* `--config_path` points at the checkpoint's `train_config.json` (not `config.json`). It carries the original `--dataset.repo_id`, `--output_dir`, etc. — you don't need to re-pass them unless overriding.
* If you re-run with the **same** `--output_dir` and **without** `--resume`, contents are **overwritten** — so always add `--resume=true` when continuing.

### B. Resume from the Hub (new VM, or after Colab killed)

If you pushed checkpoints (`--save_checkpoint_to_hub true` or manual `huggingface-cli upload`), the Hub is your resume source:

```bash
!lerobot-train \
  --config_path=your-hf-username/your-policy \
  --resume=true \
  --steps=80000   # optionally extend
```

How it works: the latest `checkpoints/<step>/` on the Hub is downloaded and training continues there, new checkpoints lineage onto the same repo. See `.venv/.../lerobot/jobs/hf.py:317 _build_resume_job` for details.

### C. Resume checklist (save yourself a headache)

* Keep `--dataset.repo_id` consistent — resuming with a different dataset is not supported (start a new `output_dir`).
* Keep `--policy.type` same (ACT) — architecture must match.
* If training stopped at 20000 but you wanted 50000, re-run with `--resume=true --steps=50000` (or higher) — it picks up from 20000.
* Checkpoints are every `save_freq` steps — if you had `save_freq=5000` and stopped at 23000, the latest is `20000`.

> **Dataset resume vs training resume:** dataset resume (§ in `05_DATA_COLLECTION.md`) re-runs the *recorder* with same `--repo-id` to append episodes. Training resume above re-runs `lerobot-train` with `--resume` to continue *optimization* from a checkpoint. They are independent — you can resume one without the other.

---

## 6. Troubleshooting — concrete

| Symptom | Likely cause | Fix |
|---|---|---|
| `CUDA out of memory` | `batch_size` too large for T4 (16 GB) | Lower `--batch_size 8 → 4 → 2` |
| `Dataset not found` / 401 | Private dataset, not logged in | `huggingface-cli login` + token with read; or make dataset public |
| `No module named lerobot` | Notebook didn't install `lerobot==0.6.1` | Re-run Cell 1, restart runtime |
| `Can't resume — output_dir exists` | Forgot `--resume` | Add `--resume=true` + `--config_path` |
| `Train loss NaN` | LR too high or `batch_size` 1 + noisy data | Use preset LR, `batch_size ≥4`, check dataset has no all-black frames (`visualize_dataset`) |
| `Upload failed` | `policy.repo_id` typo or no write token | Create repo first at `huggingface.co/new`, ensure token has `write` |

---

## 7. What's next?

* Pushed your `your-policy`? Test it live via `06_INFERENCE.md` §3 — start with `enable_robot:=false` (dry-run), then `true`.
* Want to iterate? Add more episodes via `05_DATA_COLLECTION.md` resume, then train a v2: `your-policy-v2` with more `steps`.

## Credits

Training pipeline is `lerobot`'s `lerobot-train` with ACT preset — dataset format is exactly what `lerobot-ros2-recorder.py` produces, so no conversion needed.
