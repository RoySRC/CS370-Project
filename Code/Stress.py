import gzip, pickle, sys, mmap, os
import numpy as np
import torch

import neuralnetworks_pytorch as nn


class Stress:

  def __init__(self):
    self.structure = [[625, 463, 607, 540, 994, 659, 832, 544, 808, 551, 655, 840]]
    self.batch_size = 1000
    self.learning_rate = 0.001
    self.n_iters = 20

    # Generate training and testing set
    with gzip.open('mnist.pkl.gz', 'rb') as f:
      train_set, valid_set, test_set = pickle.load(f, encoding='latin1')
    self.Xtrain = train_set[0].reshape((-1, 1, 28, 28))
    self.Ttrain = train_set[1]
    self.Xtest = test_set[0].reshape((-1, 1, 28, 28))
    self.Ttest = test_set[1]

    self.FinalWeight = None
    self.computeErrorFlag = False # initially set to false


  def Test(self, baseline = False):
    for i, nh in enumerate(self.structure):
      nnet_classify = nn.NeuralNetworkClassifier_Pytorch(np.prod(self.Xtrain.shape[2:]),
                                                         nh,
                                                         10,
                                                         relu=False,
                                                         gpu=True,
                                                         n_conv_layers=0,
                                                         windows=[],
                                                         strides=[],
                                                         input_height_width=None)

      training_accuracy = nnet_classify.train(self.Xtrain,
                                              self.Ttrain,
                                              self.Xtest,
                                              self.Ttest,
                                              self.n_iters,
                                              self.batch_size,
                                              self.learning_rate)

      # get the final weights and compare to make sure they are correct
      # if the weights are not within 2.22*10^-16, then set the
      # computeErrorFlag.
      self.FinalWeight = nnet_classify.dumpWeights()
      if not baseline:
        original = np.load("WEIGHT.npy", allow_pickle=True)
        _norm_ = np.linalg.norm([np.linalg.norm(i) for i in (original-self.getWeight())])
        print("Tensor Difference Norm:  ", _norm_)
        self.computeErrorFlag = False if _norm_ <= sys.float_info.epsilon else True

    # Unload everything from the GPU
    torch.cuda.empty_cache()

  '''
    Return the weights in the neural network as a numpy array
  '''
  def getWeight(self):
    return [fw.weight.data.cpu().numpy() for fw in self.FinalWeight]

  ''''
    Save the weights as a numpy array
  '''
  def saveWeight(self):
    _array_ = self.getWeight()
    np.save("WEIGHT", _array_)

if __name__ == "__main__":
  print("Stress process started with PID: ", os.getpid())
  stress = Stress()
  stress.Test()

  if not stress.computeErrorFlag:
    with open('/tmp/mmap.stress', 'r+b') as f:
      mm = mmap.mmap(f.fileno(), 0)
      mm.seek(0)
      mm[:] = "1".encode()
      mm.close()