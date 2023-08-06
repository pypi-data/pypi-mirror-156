import os

import torch
import torch_xla
import torch_xla.core.xla_model as xm

import torch
from transformers import AutoConfig, AutoModel, AutoTokenizer, AutoModelForCausalLM, TFAutoModelForCausalLM
import random
import time

def get_emb(model, tokenizer, context):
    # Load Transformer Embeddings
    wte_w = model.transformer.wte.weight
    wpe_w = model.transformer.wpe.weight
    # Get ids
    input_ids = torch.tensor(tokenizer.encode(context))     # str --> list --> tensor
    input_length = input_ids.size()[0]
    pos_ids = torch.arange(0, input_length, dtype=torch.long)
    # Get Embeddings
    tok_emb = wte_w[input_ids]
    pos_emb = wpe_w[pos_ids]
    # Retrun Embeddings
    return tok_emb, pos_emb

def run(checkpoint):
    device = xm.xla_device()
    config = AutoConfig.from_pretrained(checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = AutoModelForCausalLM.from_config(config, torch_dtype=torch.float16).to(device)

    wte_w = model.transformer.wte.weight
    wpe_w = model.transformer.wpe.weight


    sample_32 = 'Hamlet is considered among the most powerful and influential works of world literature, with a story capable of seemingly endless retelling and adaptation by others. It was one'
    sample_64 = 'Hamlet is considered among the most powerful and influential works of world literature, with a story capable of seemingly endless retelling and adaptation by others. It was one of Shakespeares most popular works during his lifetime and still ranks among his most performed, topping the performance list of the Royal Shakespeare Company and its predecessors in a'
    sample_128 = 'Hamlet is considered among the most powerful and influential works of world literature, with a story capable of seemingly endless retelling and adaptation by others. It was one of Shakespeares most popular works during his lifetime and still ranks among his most performed, topping the performance list of the Royal Shakespeare Company and its predecessors in Stratford-upon-Avon since 1879. It has inspired many other writers—from Johann Wolfgang von Goethe and Charles Dickens to James Joyce and Iris Murdoch—and has been described as the worlds most filmed story after Cinderella. The story of Shakespeares Hamlet was derived from the legend of Amleth,'
    samples = [sample_32, sample_64, sample_128]

    input_token_len = [32, 64, 128]
    output_token_len = [1, 4, 16, 64, 256]
    test_num = 3

    tok_emb, pos_emb = get_emb(model, tokenizer, context=samples[0])
    attn_in = tok_emb + pos_emb
    output = model(inputs_embeds=tok_emb, use_cache=True, output_hidden_states=True, output_attentions=True)

    f = open('result','w')

    for idx, i_len in enumerate(input_token_len):
      for o_len in output_token_len:

        avg_latency = 0.0
        for i in range(test_num):
          tok_emb, pos_emb = get_emb(model, tokenizer, context=samples[idx])
          attn_in = tok_emb + pos_emb
          latency = 0.0
          for j in range(o_len):
            if j == 0:
              input_length = attn_in.size()[0]
              pos_ids = torch.arange(0, input_length, dtype=torch.long)
              pos_emb = wpe_w[pos_ids]
              tok_emb = attn_in - pos_emb
            
            start_time = time.monotonic()
            output = model(inputs_embeds=tok_emb, use_cache=True, output_hidden_states=True, output_attentions=True)
            end_time = time.monotonic()
            latency += (end_time-start_time)*1000.0

            input_length += 1
            gen_tok = random.randint(1, 49999)
            tok_emb = torch.cat([tok_emb, wte_w[gen_tok].view(1, -1)], dim=0)
          avg_latency += latency
     
        avg_latency = avg_latency/float(test_num)
        print(f"input_len : {i_len}, output_len : {o_len}, latency : {latency}")
        f.write(f"input_len : {i_len}, output_len : {o_len}, latency : {latency}\n")


