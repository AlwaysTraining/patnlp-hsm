# set up relevant environment variables
export PYRO_SERIALIZERS_ACCEPTED="pickle"
export PYRO_SERIALIZER="pickle"

# set up Pyro nameserver
python -m Pyro4.naming -n 0.0.0.0 &

# set up dispacher
python -m gensim.models.lda_dispatcher &

# set up workers
python -m gensim.models.lda_worker &
python -m gensim.models.lda_worker &

# now run ldalearner.py
