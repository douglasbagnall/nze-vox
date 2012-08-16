.PHONY: all voxforge-test

.SECONDARY:

all::

export LD_LIBRARY_PATH += /usr/local/lib

TRAIN_N = 100
TEST_N = 50

EXTRA_WORDS = $(CURDIR)/dict/wordlists/wellknown-10k.txt
DICTIONARY = $(CURDIR)/dict/espeak-corpus+10k.txt
CMU_DICTIONARY = $(CURDIR)/dict/cmu-corpus+10k.txt

SPHINXTRAIN_BIN = $(CURDIR)/sphinxtrain-bin
SPHINXTRAIN_PYTHON = $(CURDIR)/sphinxtrain-python
SPHINXTRAIN_PERL = $(CURDIR)/sphinxtrain-perl
MODEL_DIR = $(CURDIR)/am

BW = $(SPHINXTRAIN_BIN)/bw

MODEL = hub4_wsj_sc_3s_8k.cd_semi_5000

MODEL_ORIG = $(MODEL_DIR)/$(MODEL)

dict/%-corpus+10k.txt:
	./generate-dict $* corpora/16k/etc/vocab $(EXTRA_WORDS) > $@ 2>$@.rej

#rebuild all the 16k sampled files and their indexes.
corpora/16k/resampled-files-all-in-place:
	mkdir -p $(@D)
	./resample-all.py --force
	touch $@

#set up training and test subcorpora
corpora/resampled/%/populated: corpora/16k/resampled-files-all-in-place
	mkdir -p corpora/resampled/
	./subcorpus.py $* $(TRAIN_N) $*/test $(TEST_N)
	echo $*: $(TRAIN_N) $*/test: $(TEST_N) > $@


# copy the model
corpora/resampled/%/$(MODEL): corpora/resampled/%/populated
	cp -rl $(MODEL_ORIG) $@

%/have_mfc: %/populated
	sphinx_fe -argfile $(MODEL_ORIG)/feat.params \
	        -samprate 16000 -c $(@D)/etc/fileids \
		-di $(@D)/wav -do $(@D)/wav -ei wav -eo mfc -mswav yes
	touch $@

%/$(MODEL)/mdef.txt: %/$(MODEL)
	pocketsphinx_mdef_convert -text $</mdef $@

%/mixture_weights: %
	python $(SPHINXTRAIN_PYTHON)/sendump.py $^/sendump $@


%/done_bw: %/have_mfc $(DICTIONARY)  %/$(MODEL)/mixture_weights  %/$(MODEL)/mdef.txt %/populated
	cd $(@D) && \
	$(BW) \
	 -ts2cbfn .semi. \
	 -feat 1s_c_d_dd \
	 -svspec 0-12/13-25/26-38 \
	 -hmmdir $(MODEL) \
	 -moddeffn $(MODEL)/mdef.txt \
	 -cmn current \
	 -agc none \
	 -dictfn $(DICTIONARY) \
	 -ctlfn ./etc/fileids \
	 -cepext mfc \
	 -lsnfn ./etc/transcription \
	 -accumdir ./
	touch $@

%/done_mapadapt: %/done_bw %/$(MODEL)
	cd $(@D) && \
	$(SPHINXTRAIN_BIN)/map_adapt \
	 -meanfn $(MODEL_ORIG)/means \
         -varfn $(MODEL_ORIG)/variances \
	 -mixwfn $(MODEL_ORIG)/mixture_weights \
	 -tmatfn $(MODEL_ORIG)/transition_matrices \
	 -accumdir . \
	 -mapmeanfn ./$(MODEL)/means \
	 -mapvarfn ./$(MODEL)/variances \
	 -mapmixwfn ./$(MODEL)/mixture_weights \
	 -maptmatfn ./$(MODEL)/transition_matrices
	touch $@

%/done_sendump:
	cd $(@D) && \
	$(SPHINXTRAIN_BIN)/mk_s2sendump \
	    -pocketsphinx yes \
	    -moddeffn ./$(MODEL)/mdef.txt \
	    -mixwfn ./$(MODEL)/mixture_weights \
	    -sendumpfn ./$(MODEL)/sendump
	touch $@


%/do_adapt_test:
	cd $(@D) && \
	pocketsphinx_batch \
	 -adcin yes \
	 -cepdir test \
	 -cepext .wav \
	 -ctl test/fileids \
	 -lm $(CURDIR)/lm/language_model.arpaformat.DMP \
	 -dict $(CMU_DICTIONARY) \
	 -hmm $(MODEL_ORIG) \
	 -hyp test/before.hyp

	cd $(@D) && \
	pocketsphinx_batch \
	 -adcin yes \
	 -cepdir test \
	 -cepext .wav \
	 -ctl test/fileids \
	 -lm $(CURDIR)/lm/language_model.arpaformat.DMP \
	 -dict $(DICTIONARY) \
	 -hmm $(MODEL) \
	 -hyp test/adapted.hyp

	cd $(@D) && \
	$(SPHINXTRAIN_PERL)/decode/word_align.pl test/transcription test/before.hyp
	cd $(@D) && \
	$(SPHINXTRAIN_PERL)/decode/word_align.pl test/transcription test/adapted.hyp
