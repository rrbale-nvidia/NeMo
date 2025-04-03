import os

import torch
import torch.distributed
from tokenizer_model import TokenizerModel

VIDEO_KEY = "video"
RECON_KEY = "reconstructions"
LATENT_KEY = "latent"
INPUT_KEY = "INPUT"
MASK_KEY = "loss_mask"
RECON_CONSISTENCY_KEY = f"{RECON_KEY}_consistency"

tm = TokenizerModel(
    jit_ckpt_pth=os.path.join(
        os.environ["HF_HOME"],
        "hub/models--nvidia--Cosmos-1.0-Tokenizer-CV8x8x8/snapshots/01f87fd67cebc32f1a2fd9e99d4e9614a6b3743b",
    )
)

device = torch.device("cuda")  # Move to GPU
input_t = torch.randn([2, 3, 33, 256, 256], dtype=torch.bfloat16, device=device)
mask_t = torch.ones_like(input_t, requires_grad=False, dtype=torch.bfloat16, device=device)
inputs = {VIDEO_KEY: input_t, MASK_KEY: mask_t}

reconstructions = torch.randn([2, 3, 33, 256, 256], dtype=torch.bfloat16, device=device)
output_batch = {RECON_KEY: reconstructions}

output = tm._training_step(inputs, 20000000)

import wandb

wandb.init()
import torch
import torch.distributed as dist

torch.distributed.init_process_group(backend='nccl')
rank = dist.get_rank()
torch.cuda.set_device(rank)  # Assign each process to a GPU

tm.validation_step(inputs, 20000000)
