﻿# -*- encoding: utf-8 -*-
# @File         : main.py
# @Date         : 2025/02/28 08:43:00
# @Author       : Eliwii_Keeya
# @Modified from: yuunnn-w, et al., 2024 -- RWKV_Pytorch

import time
import torch
from model import RWKV_RNN
from tokenizer import RWKV_TOKENIZER
from sampler import sample_logits

if __name__ == '__main__':
    args = {
        'MODEL_NAME': 'E:/Resources/Models/rwkv/RWKV-x070-World-0.1B-v2.8-20241210-ctx4096', #模型文件的名字，pth结尾的权重文件。
        'vocab_size': 65536, #词表大小
        'batch_size': 1,
        'device': 'cuda',
    }
    device = args['device']

    # 加载模型和分词器
    print("Loading model and tokenizer...")
    model = RWKV_RNN(args)
    tokenizer = RWKV_TOKENIZER()
    print("Done.")

    # 设置续写的初始字符串和参数
    BATCH_SIZE = args['batch_size']
    initial_string = "The Eiffel tower is in the city of"
    TEMPERATURE = 2.5  # 温度参数
    TOP_P = 0.1  # Top-p采样参数
    LENGTH_PER_TRIAL = 50  # 生成的长度

    # 编码初始字符串
    token = torch.tensor(tokenizer.encode(initial_string), dtype=torch.int64, device=device).expand([BATCH_SIZE, -1])
    for t in torch.unbind(token, axis=-1):
        with torch.no_grad():
            out = model.forward(t)
    else:
        token_sampled = sample_logits(out, TEMPERATURE, TOP_P).type_as(token)
        token = torch.cat((token, token_sampled.unsqueeze(1)), 1)

    start_time = time.time() # 开始计时
    for step in range(LENGTH_PER_TRIAL):  # 生成指定数量的token
        with torch.no_grad():
            out = model.forward(token_sampled)
        token_sampled = sample_logits(out, TEMPERATURE, TOP_P).type_as(token)
        token = torch.cat((token, token_sampled.unsqueeze(1)), 1)
        decoded_sequences = [tokenizer.decode(t) for t in token.tolist()]
    end_time = time.time() # 结束计时

    # 打印结果
    decoded_sequences = [tokenizer.decode(t) for t in token.tolist()]
    for i, seq in enumerate(decoded_sequences):
        print(f"Batch {i+1}: {seq}")
    
    total_time = end_time - start_time
    tokens_generated = LENGTH_PER_TRIAL * BATCH_SIZE
    speed = tokens_generated / total_time
    speed_per_batch = speed / BATCH_SIZE
    print(f"\nTotal time: {total_time:.2f} seconds")
    print(f"Tokens generated: {tokens_generated}")
    print(f"Token generation speed: {speed:.2f} tokens/second")
    print(f"Token generation speed per batch: {speed_per_batch:.2f} tokens/second")
    