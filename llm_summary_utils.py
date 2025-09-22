import openai
import time

def generate_summary(row):
    """
    Calls OpenAI API to generate a 300-500 word summary for the given file/page content.
    Returns the summary or an error message.
    """
    prompt = (
        "You are an expert construction project analyst. "
        "Summarize the following document page for a project knowledge graph. "
        "Write a clear, detailed, 300-500 word summary in professional English. "
        "Focus on key topics, entities, and any important context.\n\n"
        "Also, based on the content, classify the business type of this page as one of: 'drawing-or-map', 'financial-plan', 'schedule', 'correspondence', 'contract', 'administration', 'testing-inspection', 'closeout', or 'other'. "
        "At the end of your summary, add a line in the format: BUSINESS_TYPE: <type>\n"
        f"Document/Page Content:\n{row.get('file_content', '')}\n"
    )
    try:
        # For openai>=1.0.0
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.3,
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        time.sleep(2)
        return f"LLM ERROR: {e}"
