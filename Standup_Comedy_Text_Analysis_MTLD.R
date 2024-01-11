# Nancy Kirkman
# R Script 

# Used to measure "Lexical Diversity" of different stand-up comedy acts 
# Measures of Textual Lexical Diversity measure the ratio of original tokens to the total number of token stems 

# first off is the packages 

install.packages("qdap")
install.packages("rtools")
> library(NLP)
> library(tm)
> install.packages("qdap")
> library(qdap)
>library(qdapDictionaries)
> library(qdapRegex)
> library(RColorBrewer)
> library(qdapTools)
> library(qdap)
> install.packages("matrixStats")
> library(matrixStats)
> install.packages("ggplot2")
> library(ggplot2)
> install.packages("koRpus")
> library(koRpus)
> install.koRpus.lang(c("en"))
> library(koRpus.lang.en)


# Obtaining MTLD from Gary's "Meltdown in Trader Joes"

com_text <- "Thank you I just I want to tell you a story of my meltdown at Trader Joes. I love that place I love Trader Joes They are so thoughtful there theyre nice everybody does everybody elses job from the top to the bottom its no doubt communist. Now the people who shop at Trader Joes at least in New York City they're godless animals they are theyre pushy they put their carts in the checkout line half full and then continue to pick up items and bring it back so that theres like this empty field of carts and I do the right thing and Im standing there and last week a woman disappeared for so long that a gap developed between her cart and the rest of the line and so I filled it and prepared myself for a showdown because I knew just by the time of day, and the neighborhood what was going to come back. I just knew it was during the day so she was wealthy entitled aggressive pushy I even predicted the first two words of her sentence when she returned because she came back arm full of frozen foods meaning she went downstairs to frozen foods a ten minute round trip the audacity nay the temerity she puts them into the carriage and shes and I knew the first two words She says yeah no I was ahead of you and so I said no yeah flipped it you were ahead of me until you went shopping. you cant go downstairs for frozen foods come back with an armful and take your spot in line The best I can offer you at this point is back cutsies and thats incredibly generous But she was she was not going quietly She pushed me in the basket and went ahead and Im standing Im like is somebody gonna do something about this and then I realized I was old enough and big enough to do something on my own, so I took a stand. Which consisted of raising my fist 68 Mexican Olympic style completely inappropriate and then my slogan was this isnt fair thinking it would start a groundswell of support the people would rally behind me and chant USA silence silence except for a guy behind me who said welp here we go and then there was this eerie glow as the people raised their phones and switch from pic to vid and I would have backed down except the woman who cut me, after I said this she turns around and she says youll get over it thereby ensuring that I would never get over it I will never I know myself Ill never get over it so I picked up my basket and I jab faked left and she bit so I crossed over to get the baseline on her and she was surprised she spun and rammed me in the basket crushing my lentil chips rendering them useless
+ because theyre for dipping not for topping now at this point Im out of my mind with rage and I scream thats assault that is assault ring the bell Ive been struck and thats that is when she realized she had been out crazied and she started her retreat but she got a couple of digs in on me at the end she said fine fine go ahead of me if its that important to you it is if whats that important to me justice yeah its important to me  but you should know she says you should know that youre allowed to leave your cart in New York City that's how it works yeah no"

> corpus <- Corpus(VectorSource(com_text))
> corpus <- tm_map(corpus, content_transformer(tolower))
> corpus <- tm_map(corpus, removeWords, stopwords("en"))
> dtm <- DocumentTermMatrix(corpus)
> dtm_df <- as.data.frame(as.matrix(dtm))
> word_freq <- colSums(dtm_df)
# sorting the words by frequency in descending order
> sorted_words <- names(sort(word_freq, decreasing = TRUE))
# select the top20 words
> top_words <- sorted_words[1:20]


# lexical diversity 
# need to tokenize the text first 
tokenized <- tokenize(com_text, format = "obj", lang = "en")
MTLD(tokenized)
# Measure of Textual Lexical Diversity: Ouput 
# Total number of tokens: 616 
# Total number of types:  276

# Measure of Textual Lexical Diversity
# MTLD: 69.48 --> Trader Joes 
# Number of factors: NA 
# Factor size: 0.72 
# SD tokens/factor: 29.9 (all factors) 
# 25.67 (complete factors only)



# Gary Gulman 'Going out while broke' 

# MTLD(tokenized3)
# Language: "en"

# Total number of tokens: 457 
# Total number of types:  203

# Measure of Textual Lexical Diversity
# MTLD: 37.61 --> "Going out while broke"
#very low, probably lower than MLK's I have A Dream 
# Number of factors: NA 
# Factor size: 0.72 
# SD tokens/factor: 24.15 (all factors) 
# 24.76 (complete factors only)



# Gary Gulman "The Great Depresh" 

# gulman_mil_txt <- gulman_mil_txt(gsub("\\d", "", gulman_mil_txt))
# gulman_mil_txt <- gsub("\n", " ", gulman_mil_txt)
# gulman_mil_txt <- gsub(":", "", gulman_mil_txt)
# gg_mil_tokenized <- tokenize(gulman_mil_txt, format = "obj", lang = "en")
# MTLD(gg_mil_tokenized)
# Language: "en"

# Total number of tokens: 298 
# Total number of types:  160

#Measure of Textual Lexical Diversity
#MTLD: 73.31 --> The Great Depresh 
#Number of factors: NA 
#Factor size: 0.72 
#SD tokens/factor: 24 (all factors) 
#22.85 (complete factors only)



# Hannah Gadsby from her Netflix Special: Nanette 

# nan_text <- gsub("\\d", "", nan_text)
# nan_text <- gsub("\n", " ", nan_text)
# nan_text <- gsub(":", "", nan_text)
# nan_tokenized <- tokenize(nan_text, format = "obj", lang = "en")

# MTLD(nan_tokenized)

#MTLD(nan_tokenized)
#Language: "en"

#Total number of tokens: 526 
#Total number of types:  205

#Measure of Textual Lexical Diversity
#MTLD: 39.34 
#Number of factors: NA 
#Factor size: 0.72 
#SD tokens/factor: 25.99 (all factors) 
#26.49 (complete factors only)




# Chris Rock --> Your Mortgage Makes You Act Right 

# chris_text <- gsub("\\d", "", chris_text)
# chris_text <- gsub("\n", " ", chris_text)
# chris_text <- gsub(":", "", chris_text)
# chris_tokenized <- tokenize(chris_text, format = "obj", lang = "en")
# MTLD (chris_tokenized)

#Language: "en"

#Total number of tokens: 646 
#Total number of types:  218

#Measure of Textual Lexical Diversity
#MTLD: 42.29 
#Number of factors: NA 
#Factor size: 0.72 
#SD tokens/factor: 20.74 (all factors) 
#20.72 (complete factors only)




# Daniel Sloss --> Adorable Lesson On Animal Sexuality 
# dan_text <- gsub("\\d", "", dan_text)
# dan_text <- gsub("\n", " ", dan_text)
# dan_text <- gsub(":", "", dan_text)
# dan_tokenized <- tokenize(dan_text, format = "obj", lang = "en")
# MTLD(dan_tokenized)

#Language: "en"

#Total number of tokens: 915 
#Total number of types:  420

#Measure of Textual Lexical Diversity
#MTLD: 91.68 
#Number of factors: NA 
#Factor size: 0.72 
#SD tokens/factor: 55.63 (all factors) 
#55.42 (complete factors only)





# Ellen Degeneres Gets Anxiety In Restaurants 

# ellen_text <- gsub("\\d", "", ellen_text)
# ellen_text <- gsub("\n", " ", ellen_text)
# ellen_text <- gsub(":", "", ellen_text)
# ellen_tokenized <- tokenize(ellen_text, format = "obj", lang = "en")
# MTLD(ellen_tokenized)

# Language: "en"

#Total number of tokens: 624 
#Total number of types:  204

#Measure of Textual Lexical Diversity
#MTLD: 35 
#Number of factors: NA 
#Factor size: 0.72 
#SD tokens/factor: 20.36 (all factors) 
#20.75 (complete factors only)Language: "en"






# Gary Gulman: The Gul Takes on the Old Testament 

# last_text <- gsub("\\d", "", last_text)
# last_text <- gsub("\n", " ", last_text)
# last_text <- gsub(":", "", last_text)

# last_tokenized <- tokenize(last_text, format = "obj", lang = "en")
#MTLD(last_tokenized)

# Language: "en"

#Total number of tokens: 302 
#Total number of types:  149

#Measure of Textual Lexical Diversity
#MTLD: 48.92 
#Number of factors: NA 
#Factor size: 0.72 
#SD tokens/factor: 26.55 (all factors) 
#25.17 (complete factors only)





# John Mulaney There's a Horse In the Hospital 

# john_text <- gsub("\\d", "", john_text)
# john_text <- gsub("\n", " ", john_text)
# john_text <- gsub(":", "", john_text)
# john_tokenized <- tokenize(john_text, format = "obj", lang = "en")
# MTLD(john_tokenized)

# Language: "en"

#Total number of tokens: 652 
#Total number of types:  219

#Measure of Textual Lexical Diversity
#MTLD: 33.78 
#Number of factors: NA 
#Factor size: 0.72 
#SD tokens/factor: 22.04 (all factors) 
#21.68 (complete factors only)




