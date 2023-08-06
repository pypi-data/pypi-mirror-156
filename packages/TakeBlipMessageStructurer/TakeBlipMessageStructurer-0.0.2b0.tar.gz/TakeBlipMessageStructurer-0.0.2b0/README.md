# TakeBlipMessageStructurer Package
_Data & Analytics Research_

## Overview

Message Structurer is an AI model capable of assisting in structuring text messages.

For each message sent, a list is obtained with the main elements found in the analyzed sentence.

The elements found can be more than one word and have the following components:

- **value**: sequence of characters found in the sentence corresponding to the element
- **lowercase**: is the value found previously in lower case
- **postags**: element grammar class
- **type**: type of element found (class of entity found or postagging)

## Configure

Here are shown recommended practices to configure project on local.

## Installation

This version works in:

* PyTorch: 1.7.1
* Python: 3.6

## Conda env ##

In order to create a local environment to run the project, 
it's needed to create and activate a conda environment
- In Windows OS:

``` conda env create -f files\conda_env\ms-predict-windows.yml```

and then:

``` conda activate ms-predict-windows ```

- In Linux OS:

``` conda env create -f files/conda_env/ms-linux-windows.yml```

and then:

``` conda activate ms-predict-linux ```

### Accessing Models

In order to run Message Structure locally the three used models need to be on the project folder.

For the Embedding model the files needed are:

- *vectors_ngrams.npy
- *vectors_vocab.npy
- *vectors.npy
- *.kv

For the NER model the files needed are:

- *.pkl (for the model)
- *.pkl (for the vocab)

For the PosTagging model the files needed are:

- *.pkl (for the model)
- *.pkl (for the vocab)

## Run

To run the Message Structurer is possible in two ways: for a single sentence e for a batch of sentences.

### Sentence 
To run for a single sentence on the command line:

```
python run.py --embedding_path *.kv --postag_model_path *.pkl --postag_label_path *.pkl --ner_model_path *.pkl --ner_label_path *.pkl --input_sentence "moro atualmente em Contagem"
```

### Batch
For a batch example you will need a json file as follows:

```
{"Sentences": [{"id": 1, "sentence": "sentence_1"}, {"id": 2, "sentence": "sentence_2"}]}
```

To run for a batch of sentences on the command line:
```
python run.py --embedding_path *.kv --postag_model_path *.pkl --postag_label_path *.pkl --ner_model_path *.pkl --ner_label_path *.pkl --path_sentences *.json
```