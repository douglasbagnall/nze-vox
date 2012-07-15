#!/bin/bash -e

ROOT=$(git rev-parse --show-toplevel)

cd $ROOT

#MODEL_DIR=model/hmm/wsj1
#mkdir -p `dirname $MODEL_DIR`


TRAIN_SUBDIR=voxforge-train
TEST_SUBDIR=voxforge-test

TRAIN_DIR=$ROOT/corpora/resampled/$TRAIN_SUBDIR
TEST_DIR=$ROOT/corpora/resampled/$TEST_SUBDIR

TRAIN_N=100
TEST_N=40

if [[ ! -f $TRAIN_DIR/PROMPTS ]] ; then
    python voxforge.py $TRAIN_SUBDIR $TRAIN_N $TEST_SUBDIR $TEST_N
fi

cp -r ~/src/pocketsphinx-extra/model/hmm/en_US/wsj1/ $TRAIN_DIR

cd $TRAIN_DIR

sphinx_fe -argfile wsj1/feat.params \
        -samprate 16000 -c fileids \
       -di . -do . -ei wav -eo mfc -mswav yes

