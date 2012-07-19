.PHONY: all voxforge-test
all::

TRAIN_N = 50
TEST_N = 20

SPHINXTRAIN_BIN = $(CURDIR)/sphinxtrain-bin
SPHINXTRAIN_PYTHON = $(CURDIR)/sphinxtrain-python
SPHINXTRAIN_PERL = $(CURDIR)/sphinxtrain-perl
MODEL_DIR = $(CURDIR)/pocketsphinx-extra/model/hmm/en_US/

BW = $(SPHINXTRAIN_BIN)/bw

MODEL = wsj1

voxforge-test: corpora/resampled/voxforge/PROMPTS

corpora/resampled/%/PROMPTS:
	mkdir -p corpora/resampled/
	python voxforge.py $* $(TRAIN_N) $*/test $(TEST_N)

corpora/resampled/%/$(MODEL):
	cp -rl $(MODEL_DIR)/$(MODEL) $@

%/have_mfc: %/PROMPTS
	sphinx_fe -argfile $(MODEL_DIR)/$(MODEL)/feat.params \
	        -samprate 16000 -c $(@D)/fileids \
		-di $(@D) -do $(@D) -ei wav -eo mfc -mswav yes
	touch $@

%/mdef.txt: %/mdef %
	pocketsphinx_mdef_convert -text $< $@

%/mixture_weights: %/sendump
	python $(SPHINXTRAIN_PYTHON)/sendump.py $^ $@


%/done_bw: %/have_mfc  $(MODEL_DIR)/$(MODEL)/mixture_weights  $(MODEL_DIR)/$(MODEL)/mdef.txt %/PROMPTS
	cd $(@D) && \
	$(BW) \
	 -hmmdir $(MODEL_DIR)/$(MODEL) \
	 -moddeffn $(MODEL_DIR)/$(MODEL)/mdef.txt \
	 -feat s2_4x \
	 -cmn current \
	 -agc none \
	 -dictfn ./words.dic \
	 -ctlfn ./fileids \
	 -cepext mfc \
	 -lsnfn ./transcription \
	 -accumdir ./ \
         -ts2cbfn .semi.
	touch $@

%/done_mapadapt: %/done_bw %/$(MODEL)
	cd $(@D) && \
	$(SPHINXTRAIN_BIN)/map_adapt \
	 -meanfn $(MODEL_DIR)/$(MODEL)/means \
         -varfn $(MODEL_DIR)/$(MODEL)/variances \
	 -mixwfn $(MODEL_DIR)/$(MODEL)/mixture_weights \
	 -tmatfn $(MODEL_DIR)/$(MODEL)/transition_matrices \
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
	 -dict ./test/words.dic \
	 -hmm $(MODEL_DIR)/$(MODEL) \
	 -hyp test/before.hyp

	cd $(@D) && \
	pocketsphinx_batch \
	 -adcin yes \
	 -cepdir test \
	 -cepext .wav \
	 -ctl test/fileids \
	 -lm $(CURDIR)/lm/language_model.arpaformat.DMP \
	 -dict ./test/words.dic \
	 -hmm $(MODEL) \
	 -hyp test/adapted.hyp

	cd $(@D) && \
	$(SPHINXTRAIN_PERL)/decode/word_align.pl test/transcription test/before.hyp
	cd $(@D) && \
	$(SPHINXTRAIN_PERL)/decode/word_align.pl test/transcription test/adapted.hyp
