Prompt instructions file:

## Usage Principles
- Generate sora videos in segments based on the Sora prompts in the storyboard, then concatenate them.
- For each shot, check the `Input First Frame` field in the storyboard. If it is "Yes", extract the last frame of the previous segment and use it as the `input_reference` for the current segment. If "No", generate without a reference frame.
- Save generated sora videos and images in a separate subdirectory under outputs/ (e.g., `outputs/topic_name/`), named `shot_<n>.mp4` and `frame_<n>.png`, to avoid filename conflicts.

## Operational Workflow (Example)
1. Create a separate subdirectory for this generation within the outputs folder (e.g., `outputs/topic_name/`), and save all subsequent outputs in this subdirectory.
2. Call the storyboard-designer custom agent to create a storyboard and save it as `storyboard.md`.
3. Call the storyboard-reviewer custom agent to review the storyboard and provide improvement suggestions.
4. Have the storyboard-designer custom agent modify the storyboard based on the review suggestions.
5. Generate sora Shot 1 (no reference frame) and save as `shot_1.mp4`.
6. Extract the last frame of Shot 1 and save as `frame_1.png`.
7. For Shot 2 and subsequent shots:
    a. Check `Input First Frame` in `storyboard.md`.
    b. If "Yes", use the previous shot's last frame (e.g., `frame_1.png`) as `input_reference`.
    c. If "No", do not use `input_reference`.
    d. Generate the shot and save as `shot_<n>.mp4`.
    e. Extract the last frame and save as `frame_<n>.png` (for potential use in the next shot).
8. Repeat until all shots are completed.
9. Concatenate all MP4 files in chronological order without re-encoding to generate the final video.

## Result Handling Requirements
- Create a new subdirectory with the topic name before each execution.
- Immediately save the last frame PNG after generating each segment, named `frame_<shot>.png`, in the same directory as the corresponding MP4.
- If character or scene drift occurs, reduce camera movement or increase reference frame weight, and explicitly declare to maintain feature consistency.

## Final Summary Report
At the end of the process, output a summary containing:
- **Resolution**: The video resolution used.
- **Shot Count**: Total number of shots generated.
- **Error Log**: Whether any errors occurred during generation and how they were handled.
- **Final Output Path**: The full path to the final concatenated video file.
