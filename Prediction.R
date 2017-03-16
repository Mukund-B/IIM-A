#Set the working directory to the folder containing final_df.csv
setwd("M:/Documents/IIM-A Hackathon")
data <- read.csv("final_df.csv",na.strings = c("", " "))
data$z.score_2011 <- as.factor(data$z.score_2011)
data$z.score_2012 <- as.factor(data$z.score_2012)
data$z.score_2013 <- as.factor(data$z.score_2013)
data$z.score_2014 <- as.factor(data$z.score_2014)
data$z.score_2015 <- as.factor(data$z.score_2015)
train1 <- data.frame(data$ID)
train2 <- data.frame(data$ID)
train3 <- data.frame(data$ID)
test <- data.frame(data$ID)

getMSE <- function(pred,actual){
  mse <- mean((pred-actual)^2)
  return (mse)
}
getSSE <- function(pred,actual){
  sse <- sum((pred-actual)^2)
  return (sse)
}
log <- function(x) ifelse(x <= 0, 0, base::log(x))
train1$Stock <- data$Stock_2014
train1$S_1 <- data$Stock_2013
train1$S_2 <- data$Stock_2012
train1$Sector <- data$Sector
train1$ROE <- data$ROE_2013
train1$ROA <- data$ROA_2013
train1$Trend_1 <- data$Trend_2013
train1$Trend_2 <- data$Trend_2012
train1$Sent <- data$Sent_2013
train1$Vader <- data$Vader_2013
train1$Share <- data$Share_2013
train1$data.ID <- NULL

train2$Stock <- data$Stock_2013
train2$S_1 <- data$Stock_2012
train2$S_2 <- data$Stock_2011
train2$Sector <- data$Sector
train2$ROE <- data$ROE_2012
train2$ROA <- data$ROA_2012
train2$Trend_1 <- data$Trend_2012
train2$Trend_2 <- data$Trend_2011
train2$Sent <- data$Sent_2012
train2$Vader <- data$Vader_2012
train2$Share <- data$Share_2012
train2$data.ID <- NULL

train3$Stock <- data$Stock_2012
train3$S_1 <- data$Stock_2011
train3$S_2 <- data$Stock_2010
train3$Sector <- data$Sector
train3$ROE <- data$ROE_2011
train3$ROA <- data$ROA_2011
train3$Trend_1 <- data$Trend_2011
train3$Trend_2 <- data$Trend_2010
train3$Sent <- data$Sent_2011
train3$Vader <- data$Vader_2011
train3$Share <- data$Share_2011
train3$data.ID <- NULL

test$Stock <- data$Stock_2015
test$S_1 <- data$Stock_2014
test$S_2 <- data$Stock_2013
test$Sector <- data$Sector
test$ROE <- data$ROE_2014
test$ROA <- data$ROA_2014
test$Trend_1 <- data$Trend_2014
test$Trend_2 <- data$Trend_2013
test$Sent <- data$Sent_2014
test$Vader <- data$Vader_2014
test$Share <- data$Share_2014
test$data.ID <- NULL


train <- na.omit(rbind(train1,train2,train3))
stock <- train$Stock
sect <- train$Sector
z <- train$z
T1 <- train$Trend_1
T2 <- train$Trend_2
Sent <- train$Sent
Vader <- train$Vader

train$Stock <-NULL
train$Sector <- NULL
train$z <- NULL
train$Trend_1 <- NULL
train$Trend_2 <- NULL
train$Sent <- NULL
train$Vader <- NULL

scaled.train <- data.frame(scale(train))
colMeans(scaled.train)
scaled.train$Sector <- sect
scaled.train$z <- z
scaled.train$Trend_1 <- T1
scaled.train$Trend_2 <- T2
scaled.train$Stock <- stock
scaled.train$Sent <- Sent
scaled.train$Vader <- Vader

test <- na.omit(test)
sect <- test$Sector
stock <- test$Stock
z <- test$z
T1 <- test$Trend_1
T2 <- test$Trend_2
Sent <- test$Sent
Vader <- test$Vader

test$Sector <- NULL
test$z <- NULL
test$Trend_1 <- NULL
test$Trend_2 <- NULL
test$Stock <- NULL
test$Sent <- NULL
test$Vader <- NULL

scaled.test <- data.frame(scale(test))
colMeans(scaled.test)
scaled.test$Sector <- sect
scaled.test$z <- z
scaled.test$Trend_1 <- T1
scaled.test$Trend_2 <- T2
scaled.test$Stock <- stock
scaled.test$Sent <- Sent
scaled.test$Vader <- Vader

library('randomForest')
stockRF = randomForest(Stock ~ S_1 + S_2+Sector+Trend_1+Trend_2+ROE+ROA+Sent,data = scaled.train,ntree=15000)
Prediction <- predict(stockRF,newdata=scaled.test)
Prediction[Prediction<0] <- 0
getSSE(Prediction,scaled.test$Stock)
getMSE(Prediction,scaled.test$Stock)
Actual <- scaled.test$Stock
result = cbind(Prediction,Actual)
write.csv(result,'Output.csv')
