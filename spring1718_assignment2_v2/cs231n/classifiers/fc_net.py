from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian centered at 0.0 with               #
        # standard deviation equal to weight_scale, and biases should be           #
        # initialized to zero. All weights and biases should be stored in the      #
        # dictionary self.params, with first layer weights                         #
        # and biases using the keys 'W1' and 'b1' and second layer                 #
        # weights and biases using the keys 'W2' and 'b2'.                         #
        ############################################################################

        W1 = np.random.randn(input_dim,hidden_dim)*weight_scale
        b1 = np.zeros(hidden_dim)
        W2 = np.random.randn(hidden_dim,num_classes)*weight_scale
        b2 = np.zeros(num_classes)
        self.params["W1"] = W1
        self.params["b1"] = b1
        self.params["W2"] = W2
        self.params["b2"] = b2

        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################


    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        
        W1 = self.params["W1"]
        b1 = self.params["b1"]
        W2 = self.params["W2"]
        b2 = self.params["b2"]

        # Z1 = np.dot(X,W1) + b1
        #A1 = np.maximum(Z1,0)
        out,cache1 = affine_forward(X, W1, b1)

        out,cache2 = relu_forward(out)

        out,cache3 = affine_forward(out, W2, b2)

        scores = out

        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################

        loss, dout = softmax_loss(scores, y)
        # add L2 regularization
        loss += 0.5*self.reg*(np.sum(W1*W1)+np.sum(W2*W2))

        dout,dW2,db2 = affine_backward(dout, cache3)

        grads["W2"] = dW2 + self.reg*W2
        grads["b2"] = db2

        dout = relu_backward(dout, cache2)
        dout, dW1, db1 = affine_backward(dout, cache1)
        grads["W1"] = dW1 + self.reg*W1
        grads["b1"] = db1




        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch/layer normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch/layer normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=1, normalization=None, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=1 then
          the network should not use dropout at all.
        - normalization: What type of normalization the network should use. Valid values
          are "batchnorm", "layernorm", or None for no normalization (the default).
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.normalization = normalization
        self.use_dropout = dropout != 1
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution centered at 0 with standard       #
        # deviation equal to weight_scale. Biases should be initialized to zero.   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to ones and shift     #
        # parameters should be initialized to zeros.                               #
        ############################################################################
        temp_input_dim=input_dim
        hidden_size = len(hidden_dims)
        for i in range(hidden_size):
            W =(np.random.randn(temp_input_dim,hidden_dims[i]))*weight_scale
            b = np.zeros(hidden_dims[i])
            self.params["W"+str(i+1)]=W
            self.params["b"+str(i+1)]=b
            temp_input_dim=hidden_dims[i]
            if self.normalization=="batchnorm":
                if i+1<hidden_size:# 要画出图来看，最后一层没有batchnorm 例如： w1,b1->gamma1,beta1->relu->w2,b2->gamma2,beta2->relu->w3,b3->softmax
                    self.params["gamma"+str(i+1)]=np.ones(hidden_dims[i])
                    self.params["beta"+str(i+1)]=np.zeros(hidden_dims[i])
            if self.normalization=="layernorm":
                if i+1<hidden_size:
                    self.params["gamma"+str(i+1)]=np.ones(hidden_dims[i])
                    self.params["beta"+str(i+1)]=np.zeros(hidden_dims[i])
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.normalization=='batchnorm':
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]
        if self.normalization=='layernorm':
            self.bn_params = [{} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)


    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.normalization=='batchnorm':
            for bn_param in self.bn_params:
                bn_param['mode'] = mode
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        
        N = X.shape[0]
        out=X
        caches =[]
        hidden_size = self.num_layers-1
        for i in range(hidden_size):

            W = self.params["W"+str(i+1)]

            b = self.params["b"+str(i+1)]
            out,cache = affine_forward(out, W, b)
            caches.append(cache)
           
            if i<hidden_size-1:
                if self.normalization=='batchnorm':
                    gamma = self.params["gamma"+str(i+1)]
                    beta = self.params["beta"+str(i+1)]
                    out,cache = batchnorm_forward(out, gamma, beta, self.bn_params[i])
                    caches.append(cache)
                if self.normalization=='layernorm':
                    gamma = self.params["gamma"+str(i+1)]
                    beta = self.params["beta"+str(i+1)]
                    out,cache = layernorm_forward(out, gamma, beta, self.bn_params[i])
                    caches.append(cache)
                out,cache = relu_forward(out)
                caches.append(cache)
                if self.use_dropout:
                    out, cache = dropout_forward(out,self.dropout_param)
                    caches.append(cache)
        scores = out

        
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch/layer normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, dout = softmax_loss(scores, y)
        loss_weight_part=0.0
        for i in range(hidden_size-1,-1,-1):

            W = self.params["W"+str(i+1)]
            b = self.params["b"+str(i+1)]
            loss_weight_part+=np.sum(W*W)
            cache = caches.pop()

            dout,dW,db = affine_backward(dout, cache)

            grads["W"+str(i+1)] = dW + self.reg*W
            grads["b"+str(i+1)] = db

            if i>0:
                if self.use_dropout:
                    cache = caches.pop()
                    dout = dropout_backward(dout, cache)
                cache = caches.pop()
                dout = relu_backward(dout, cache)
                if self.normalization=='batchnorm':
                    cache = caches.pop()
                    dout, dgamma, dbeta = batchnorm_backward(dout, cache)
                    grads["gamma"+str(i)] = dgamma #具体是i+1,还是i,一定要计算好，可以在草稿纸上画出图来，就知道是i还是i+1了
                    grads["beta"+str(i)] = dbeta
                if self.normalization=='layernorm':
                    cache = caches.pop()
                    dout, dgamma, dbeta =layernorm_backward(dout, cache)
                    grads["gamma"+str(i)] = dgamma #具体是i+1,还是i,一定要计算好，可以在草稿纸上画出图来，就知道是i还是i+1了
                    grads["beta"+str(i)] = dbeta

        loss += 0.5 * self.reg * loss_weight_part
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads
