from similarities import BM25Similarity, BertSimilarity

class SimilarityMixin:

    def bm25_similarity(self, query, corpus, topn=5):
        sim = BM25Similarity()
        if None in corpus:
            corpus = [c for c in corpus if c is not None]
            corpus += ["null"]
        sim.add_corpus(corpus)
        res = sim.most_similar(query, topn=topn)
        res = res[0]
        return_dicts = []
        for i, record in enumerate(res):
            return_dicts.append({
                "text": record['corpus_doc'],
                "similarity_score": record['score'],
                "rank": i+1
            })

        return return_dicts
    
    def bert_similarity(self, query, corpus, topn=5):
        sim = BertSimilarity()
        corpus = [str(c) for c in corpus]
        sim.add_corpus(corpus)
        res = sim.most_similar(query, topn=topn)
        res = res[0]
        return_dicts = []
        for i, record in enumerate(res):
            return_dicts.append({
                "text": record['corpus_doc'],
                "similarity_score": record['score'],
                "rank": i+1
            })

        return return_dicts


    # no nerual network method
    def edit_distance_similarity(self, text1, text2):
        """
        Compute the edit distance of two texts.
        """
        #todo
        pass
    
    # semantic baseline
    def SIF_similarity(self, text1, text2):
        """
        Compute the similarity of two texts using the SIF algorithm.
        """
        #todo
        pass

    def avg_w2v_similarity(self, text1, text2):
        pass



    # sentence-bert
    def sentence_bert_similarity(self, text1, text2):
        """
        Compute the similarity of two texts using the sentence-bert algorithm.
        """
        #todo
        pass


    def sbert_with_context_similarity(self, text1, text2):
        """
        Compute the similarity of two texts using the sentence-bert algorithm with context.
        """
        #todo
        pass