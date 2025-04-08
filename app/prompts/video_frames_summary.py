def get_summary_prompt(data):

    summary_prompt = f"""
Generate a short, high-level summary (3-5 sentences) describing the main content of a video based on vision model analysis (e.g., YOLO, CLIP, Detectron). Focus on key objects, actions, and scene context.

At the end, summarize all the summaries to make a general summary.


Vision model analysis result:

{data}
"""
    return summary_prompt
