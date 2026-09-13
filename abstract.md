**Introduction**

In order to analyze players' performance in basketball, it is essential to have a system capable of tracking the players, maintaining their identity throughout the game. State of the art tracking algorithms, such as BoTSORT or OC-SORT, are design to track objects throughout occlusions, but they are not specifically tailored to sports, so sometimes they fail to mantain the identity of the players, especially in long scenarios, such as an entire quarter. 

This project aims to develop a system that tracks basketball players in order to obtain metrics that can be used to analyze their performance. The target audience of the project is non-professional basketball teams that are able to use the system without making large investments.

In this work, we present a system that uses a single camera video of the game, the players' jersey numbers and the approximate colors of the uniforms to track the players, maintaining their identity using static information. The tracking information is used to obtain heatmaps of players' positions and ball possesion graphs, illustrating the type of metrics that can be built on top of the tracking results.

**Tracking goal**

The main goal of the tracking system is to avoid identity fragmentation, which occurs when the same player is assigned different identifiers throughout the game, and to avoid identity swaps, which occur when a player is assigned the identifier of another player. While it is important to detect players in every frame, it is even more important to maintain a consistent identifier per player that does not change over time. This is especially relevant in basketball, where each quarter lasts at least 10 minutes, and even a small number of identity swaps and new identifiers per minute can severely affect player statistics, making it impossible to obtain player-specific metrics for the processed video.

**Dataset and tools**

To evaluate the system, we use the SportsMOT dataset. This dataset contains annotations of player's positions and their identifiers in different videos of three different sports. Since this work focuses on basketball, only the basketball videos are used. Although frames from the train, validation and test splits are available, only the train and validation splits include annotations, so the evaluation is carried out on the validation split. All the code is implemented in Python due to the availability of libraries for tracking, OCR and visualization.

**Trackers compared**

A comparison of trackers is carried out to select the most suitable one for the system, serving as the base tracking algorithm on which the system is built. The trackers evaluated are ByteTrack, BoTSORT, OC-SORT, Deep OC-SORT and SAM2. ByteTrack and OC-SORT use only motion information to track objects; they rely on the predicted bounding boxes to create identifiers for new objects and track them throughout a video. BoTSORT and Deep OC-SORT use both motion and appearance information, so they also exploit the visual appearance of the objects within the bounding boxes to keep track of how they look and to reidentify them after occlusions. SAM2 is a more complex tracker that uses attention mechanisms to track objects.

**Metrics**

The metrics used to evaluate the trackers are IDF1, IDTP, IDFN, IDFP, IDSW and IDs created. The number of IDs created give an idea of how fragmented the trayectories are. The number of times two identities are swapped (IDSW) is also a metric to take into account. The number of frames where an object is correctly identified (IDTP), incorrectly identified (IDFP) or not identified (IDFN) is a useful indicator of the types of errors the tracker is making. IDF1 is a key metric, as it combines IDTP, IDFP and IDFN to summarize how well the tracker follows the objects while preserving their identity.

**System architecture**

The tracking system is built on top of an object tracker. In this work, BoTSORT is used as the base tracker. The system includes a jersey number reading module, which detects the jersey bounding boxes, reads the numbers, and associates them with the players predicted in the current frame. It also includes a team assigment module, which keeps track of the players' bounding boxes in the first 50 frames, and uses them to train a k-means model that classifies players into two teams using color statistics from uniform regions in the bounding boxes. The jersey number, team color, bounding box prediction, and track identifier are jointly used to keep track of the players and to reidentify them after occlusions or to detect tracking errors, such as identity swaps.

**Why BoTSORT**

After tuning trackers' hyperparameters based on the train split, the trackers are evaluated on the validation split. We see that motion-based trackers run at roughly twice the speed of motion plus appearance trackers, and SAM2 is the slowest tracker, processing 4 frames per second (BoTSORT runs at 56 fps). In terms of IDF1, SAM2 and BoTSORT are close in performance, with scores of 71.44 and 71.25 respectively, while the other trackers are in the 60-63 range. SAM2 has fewer identity swaps and creates fewer identifiers, but its much lower speed makes it an inconvenient choice for the system. Therefore, BoTSORT is chosen as the base tracker.

**Jersey number detection**

We train a YOLOv8 model to detect jersey numbers. Although we already have player bounding boxes, OCR models do not perform well when the bonding box is too large, and since players can appear in different poses, we cannot define a fixed crop that is both small enough for the OCR model to work well and large enough to consistently include the jersey number. Therefore, we train a model to detect jersey numbers. The dataset used is also annotated with ball bounding boxes, which we use to generate the ball possession graphs.

**OCR evaluation**

For the OCR module, we compare EasyOCR, PARSeq and Tesseract. We use a dataset of 3600 cropped jersey number images, with numbers from 0 to 40 and a variety of uniform colors. If anything other than numbers is detected, or nothing is detected, the prediction is considered null. PARSeq has the best results, whith the lower number of null predictions and the highest accuracy among non-null predictions. We also tried preprocessing the images to improve OCR performance, in case it helped another OCR model outperform PARSeq, but it did not improve the results and it increased processing time, so we decided not to use any preprocessing. Consequently, PARSeq is selected as the OCR model in the system.

**Team assignment**

We train a k-means model on the first 50 frames of the video, which then groups players into two teams. This method is chosen because it is fast and adds robustness to the classification in the presence of small changes in uniform color due to lighting conditions. For the image features, we tested color histograms (RGB, HSV, and only the H channel), statistics of the color channels (mean, max, and standard deviation), and a combination of both. We chose the color channel statistics because their performance was only comparable to histogram plus statistics, while being simpler and faster to compute. Since we did not have a dedicated dataset to evaluate the team assignment module, we manually inspected the results on different videos with varying uniform colors, and we tested the features within the full system, evaluating the impact on tracking metrics on SportsMOT.

**Integration logic**

In order to integrate the jersey number reading and team assigment modules with the base tracker, we first associate the detected jersey numbers with the players' bounding boxes from the tracks in the current frame. Then, we use this information, along with the team classification computed from the bounding box, to update the data associated with each track identifier. We do not assign a jersey number or team to a track until several consecutive frames support the same number or team, to avoid misclassifications due to occlusions or wrong predictions.

For each track from the base tracker, we maintain a state that includes its current jersey number and team. This state is updated at every frame according to the jersey number and team detected in the corresponding bounding box.

Using this information, the system associates the visible tracks with players in each frame based on their jersey number and team. A track is associated with a player when their jersey number and team coincide. If multiple tracks share the player's jersey number and team, the system selects the one whose center is the closest to the player's last known position. If only one player of a team remains unassigned and there is a single unassigned track from that team without a jersey number, they are associated. In addition, when a track has an associated jersey number that only appears in one of the teams, and the corresponding player is not yet associated with any track, the system also associates them.

**Final results**

The system is evaluated on the validation split of the SportsMOT dataset as a test set and we compare our approach with several state of the art trackers. We report IDF1, IDTP, IDFN, IDFP, IDSW, the number of identities created, and the processing speed. Our system runs at 23 FPS, making it a practical option for non professional teams.

In terms of identity based metrics, our system achieves the lowest number of IDFP by a large margin, while obtaining an IDF1 score close to BoTSORT and SAM2. These results reflect the design choice of prioritizing identity consistency over continuous detection. The system avoids assigning identities to players when it is uncertain, which reduces the number of IDFP, but increases the number of frames where a player is not identified (IDFN) and slightly reduces the number of frames where a player is correctly identified (IDTP) compared to the other trackers. The system also avoids identity fragmentation, as it mantains a single identity per player and correct identity swaps when they occur, allowing metrics to be computed consistently for each player.

These results are obtained on short videos of 20-40 seconds, whereas basketball games are much longer, at least 10 minutes per quarter. In longer sequences, even a small number of identity swaps and identity fragmentation can severely affect player statistics, as the system would not able to provide consistent metrics for each player. Qualitative analysis on validation videos shows that, while trackers often assign multiple identifiers to the same player and sometimes swap identities, our system tends to maintain the same identifier for each player and, when uncertain, drops the identity and later recovers it, instead of swapping it with another player. This is key to obtaining consistent metrics per player in videos that last several minutes.

**Heatmaps and the ball possession graphs**

Building on top of the tracked player identities, we derive additional metrics to analyze each player's positioning on the court and ball possession. Player positions are projected onto the court using an existing keypoint based homography estimation method, and are aggregated over time to generate individual and team heatmaps that highlight the areas of the court where each player and team spend the most time. In addition, a simple ball possession module associates the ball with the most likely player in each frame, or with no player when the ball is far from any player like when it is in the air. The association is based on the percentage of the ball bounding box in the player's bounding box. These metrics are computed by quarter, as this granularity helps to better analyze players' performance. These graphs illustrate how the proposed system can support tactical analysis and decision-making for coaches.

**Limitations**

The system limitations include scenarios where a player's jersey number is not visible for an extended period. When a player spends a long time facing sideways and the jersey number is rarely visible, it is difficult for the system to assign a jersey number to the corresponding track if it has not been observed yet. In such cases, the system can only associate the track if it is the only unassigned player of that team. Similarly, if the jersey numbers are too worn out and not clearly visible, the system may take longer to recognize them, which can delay the assignment of jersey numbers to tracks.

In these situations, the system tends to increase the number of frames in which the player is not identified, rather than risking wrong assignments, which is aligned with the design choice of prioritizing identity consistency.

**Future work**

As future work, it would be interesting to develop a user-friendly interface for coaches to easily process videos and visualize the results. Also, additional metrics such as players' speed, distance covered and time spent in different actions would provide further useful insights for coaches. 