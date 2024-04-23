from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from umap import UMAP
import numpy
from bertopic.representation import MaximalMarginalRelevance

from barchart import make_top10_bar


def cluster_comments(data, video_name):

    docs = data["comment_text"]

    len_docs = len(docs)

    mts = min_number_of_comments_for_cluster(len_docs)

    # Prepare embeddings
    sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
    print(f'Start Clustering for video {video_name}')
    embeddings = sentence_model.encode(docs, show_progress_bar=True)

    # Remove stop words ("the", "is", etc) AFTER embeddings stage:
    # Here and later comments about BERTopic include author's quotes for clarity https://github.com/MaartenGr/BERTopic/
    # "Removing stop words as a preprocessing step is not advised as the transformer-based embedding models that we use need the full context to create accurate embeddings."
    # "Instead, we can use the CountVectorizer to preprocess our documents after having generated embeddings and clustered our documents."
    vectorizer_model = CountVectorizer(stop_words="english") 


    # "As a little bonus, we can use bertopic.representation.MaximalMarginalRelevance in BERTopic to diversify words in each topic such that we limit the number of duplicate words we find in each topic"
    # "We do this by specifying a value between 0 and 1, with 0 being not at all diverse and 1 being completely diverse:"
    representation_model = MaximalMarginalRelevance(diversity=0.4)

    # Train BERTopic
    topic_model = BERTopic(vectorizer_model=vectorizer_model, embedding_model=sentence_model, representation_model=representation_model, min_topic_size = mts).fit(docs, embeddings)

    # Sometimes (particularly for large sample of 2000+ docs) algorithm generates just one topic in the first run
    # In that case - make another run:
    if len(topic_model.get_topic_info()) < 3:
        print("ONLY ONE TOPIC GENERATED - START CLUSTERING AGAIN")
        embeddings = sentence_model.encode(docs, show_progress_bar=True)

        # Train BERTopic AGAIN
        topic_model = BERTopic(vectorizer_model=vectorizer_model, embedding_model=sentence_model, representation_model=representation_model, min_topic_size = mts).fit(docs, embeddings)

    # Print number of topics generated including undistibuted
    print(len(topic_model.get_topic_info()))

    # Generate nicer looking labels and set them in our model
    topic_labels = topic_model.generate_topic_labels(nr_words=3,topic_prefix=False, word_length=15, separator=" | ")
    
    topic_model.set_topic_labels(topic_labels)

    # Make docs(i.e. comments) shorter - so that they look better on plot
    shorter_docs = make_shorter_docs(docs)

    # MAIN PLOT
    # Run the visualization with the original (already calculated) embeddings
    figure_docs = topic_model.visualize_documents(docs = shorter_docs, embeddings=embeddings, width=1200, height=750, custom_labels=True, title= "<b>Comments Clustered in Topics</b>")
    

    # Optionally: to save graph to html file:
    # figure_docs.write_html("fig_docs.html")

    # Optionally: to hide legend on plot:
    # figure_docs.update_layout(legend_visible = False)


    figure_docs.update_layout(
                            #   plot_bgcolor = "rgb(240,248,255)",
                            #   paper_bgcolor= "rgb(240,248,255)",
                              legend = dict(orientation="h",
                                            yanchor="bottom", 
                                            y=0.03,
                                            yref = "container",
                                            xanchor="center",
                                            x=0.5, 
                                            title=dict(side = "top center", text = "<b>Show/Hide a cluster</b>", font = dict(size = 14)),
                                            itemclick = "toggleothers",
                                            itemdoubleclick = "toggle",
                                            bgcolor= "AliceBlue",
                                            bordercolor="rgb(155, 178, 198)",
                                            borderwidth=2
                                            ))


    # Save generated graph to python variable:
    fig = figure_docs.to_html(full_html=False)

    # Optionally: save this fig to txt file (for an example on how_to_use page)
    # save_as_txt(fig, "static/txtfiles/fig_test.txt")
    
    # Get topics basic info in df
    topics_info = topic_model.get_topic_info()

    # Change topics name a little bit for table view (add "Topic#" and | separator)
    customize_topics_labels_for_table(topics_info)

    # Change topics name a little bit for barchart (5 words instead of 3)
    customize_topics_labels_for_barchart(topics_info)

    bar_chart = make_top10_bar(topics_info.head(11), len_docs).to_html(full_html=False)

    # Optionally: save this fig to txt file (for an example on how_to_use page)
    # save_as_txt(bar_chart, "static/txtfiles/bar_chart_test.txt")

    return fig, topics_info, bar_chart

# Depending on total number of comments it is reasonable to set adequate minimum number of comments for cluster
# The more comments video has - the higher min number of comments for cluster should be. Formula below empirically works well for this task.
def min_number_of_comments_for_cluster(n):
    k = int(round(numpy.log(n) + n/500))
    print(f'min comments per cluster: {k}')
    return k

def customize_topics_labels_for_table(dataframe):
    
    lables_list = []
    
    # Make custom topics labels and store them to list
    for old_topic_label in dataframe['Name']:
        new_topic_label_list = old_topic_label.split('_')
        
        new_topic_label = ("Topic #" + str(int(new_topic_label_list[0]) + 1) + ":" + " " 
                           + str(new_topic_label_list[1]).capitalize() + " |" + " " 
                           + str(new_topic_label_list[2]).capitalize() + " |" + " " 
                           + str(new_topic_label_list[3]).capitalize())
        lables_list.append(new_topic_label)

    # Add new topics to a new column in original df
    dataframe['Name_for_table'] = lables_list
    # Set first row name to ("Undistributed...")
    dataframe['Name_for_table'][0] = "Undistributed comments (comments that did not fall into any cluster)"
     

def make_shorter_docs(docs):
    shorter_docs = []
    for doc in docs:
        new_doc = str(doc)[:150]
        if len(doc) >= 151:
            new_doc = new_doc + "<br>" + str(doc)[150:300]
            if len(doc) >= 301:
                new_doc = new_doc + "<br>" + str(doc)[300:448] + "..."
        shorter_docs.append(new_doc)
    return shorter_docs


def customize_topics_labels_for_barchart(dataframe):
    
    lables_list = []

    # Make custom topics labels and store them to list
    for index, row in dataframe.iterrows():
        new_topic_label = "Topic #" + str(int(row['Topic']) + 1) + ":" + " "

        if row['Representation'][0] != "":
                new_topic_label = new_topic_label + str(row['Representation'][0]).capitalize()

        for i in range(1,5):
            if row['Representation'][i] != "":
                new_topic_label = new_topic_label + "," + " " + str(row['Representation'][i]).capitalize()
                    
        lables_list.append(new_topic_label)

    # Add new topics to a new column in original df
    dataframe['Name_for_barchart'] = lables_list
    # Set first row name to ("Undistributed...")
    dataframe['Name_for_barchart'][0] = "Undistributed comments (comments that did not fall into any cluster)"
    

def save_as_txt(html_element, file_path):
    with open(file_path, 'w') as txt_file:
        txt_file.write(html_element)