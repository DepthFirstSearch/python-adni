#!/bin/bash

THEANO_FLAGS=device=gpu,floatX=float32 python train4.py 1 > output_4_CV1
THEANO_FLAGS=device=gpu,floatX=float32 python train4.py 2 > output_4_CV2
THEANO_FLAGS=device=gpu,floatX=float32 python train4.py 3 > output_4_CV3
THEANO_FLAGS=device=gpu,floatX=float32 python train4.py 4 > output_4_CV4
THEANO_FLAGS=device=gpu,floatX=float32 python train4.py 5 > output_4_CV5
THEANO_FLAGS=device=gpu,floatX=float32 python train4.py 6 > output_4_CV6
THEANO_FLAGS=device=gpu,floatX=float32 python train4.py 7 > output_4_CV7
THEANO_FLAGS=device=gpu,floatX=float32 python train4.py 8 > output_4_CV8
THEANO_FLAGS=device=gpu,floatX=float32 python train4.py 9 > output_4_CV9
THEANO_FLAGS=device=gpu,floatX=float32 python train4.py 10 > output_4_CV10
