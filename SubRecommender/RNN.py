from __future__ import division, print_function, absolute_import

import tflearn
from tflearn.data_utils import to_categorical, pad_sequences
from dask import dataframe as dd 

def train_model(train,test,vocab_size,max_seq_size,npartitions=3):
    dd_train = dd.from_pandas(train, npartitions=npartitions)
    dd_test =  dd.from_pandas(test, npartitions=npartitions)

    trainX = dd_train['sub_seqs'].compute()
    trainY = dd_train['sub_label'].compute()
    testX = dd_test['sub_seqs'].compute()
    testY = dd_test['sub_label'].compute()

    # Sequence padding
    trainX = pad_sequences(trainX, maxlen=max_seq_size, value=0.)
    testX = pad_sequences(testX, maxlen=max_seq_size, value=0.)

    # Converting labels to binary vectors
    trainY = to_categorical(trainY, nb_classes=vocab_size)
    testY = to_categorical(testY, nb_classes=vocab_size)

    # Network building
    net = tflearn.input_data([None, max_seq_size])
    net = tflearn.embedding(net, input_dim=vocab_size, output_dim=128)
    net = tflearn.lstm(net, 64, dropout=0.8)
    net = tflearn.fully_connected(net, vocab_size, activation='softmax')
    net = tflearn.regression(net, optimizer='adam', learning_rate=0.001,
                             loss='categorical_crossentropy')

    # Training
    model = tflearn.DNN(net, tensorboard_verbose=0)
    model.fit(trainX, trainY, validation_set=(testX, testY), show_metric=True,
              batch_size=256)
    return model