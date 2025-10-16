import streamlit as st
import openai
from openai import OpenAI
import pyperclip

st.set_page_config(page_title="Question Generator", layout="wide")

st.title("📚 AI Question & Answer Generator")
st.markdown("Generate questions and answers based on marks, topics, and Bloom's Taxonomy levels")

# Sidebar for API Key
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
    st.markdown("---")
    st.markdown("### Bloom's Taxonomy Levels")
    st.markdown("""
    - **Remember**: Recall facts and basic concepts
    - **Understand**: Explain ideas or concepts
    - **Apply**: Use information in new situations
    - **Analyze**: Draw connections among ideas
    - **Evaluate**: Justify a stand or decision
    - **Create**: Produce new or original work
    """)

# Main input section
col1, col2 = st.columns(2)

with col1:
    marks = st.number_input("Total Marks", min_value=1, max_value=100, value=10, step=1)
    
    topics = st.text_area(
        "Topics (one per line or comma-separated)",
        height=100,
        placeholder="e.g., Data Structures, Algorithms, Database Management"
    )

with col2:
    bloom_level = st.selectbox(
        "Bloom's Taxonomy Level",
        ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
    )
    
    num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5, step=1)

# Syllabus content section
st.markdown("---")
st.subheader("📖 Syllabus Content (Optional)")
syllabus_content = st.text_area(
    "Provide detailed syllabus content (if provided, questions will be generated from this instead of topics)",
    height=150,
    placeholder="Paste your syllabus content here. If provided, this will be used instead of the topics field above.",
    help="If you provide syllabus content, it will take priority over the topics field"
)

# Additional comments section
st.subheader("💬 Additional Comments/Guidelines (Optional)")
additional_comments = st.text_area(
    "Add any specific guidelines, instructions, or preferences for question generation",
    height=100,
    placeholder="e.g., Focus on practical applications, Include diagrams descriptions, Avoid theoretical questions, etc.",
    help="These comments will be added to the prompt as additional guidelines"
)

# Example format section
st.markdown("---")
st.subheader("📝 Question & Answer Format Example")

example_format = st.text_area(
    "Provide an example of how questions and answers should be formatted",
    height=150,
    placeholder="""Example:
Q1. What is a binary search tree? (2 marks)
Answer: A binary search tree is a node-based binary tree data structure where each node has at most two children, and for each node, all elements in the left subtree are less than the node, and all elements in the right subtree are greater than the node.

Q2. Explain the time complexity of binary search. (3 marks)
Answer: Binary search has a time complexity of O(log n) because it divides the search space in half with each comparison..."""
)

# Generate button
if st.button("🚀 Generate Questions & Answers", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar!")
    elif not topics.strip() and not syllabus_content.strip():
        st.error("⚠️ Please enter either topics or syllabus content!")
    else:
        try:
            # Initialize OpenAI client
            client = OpenAI(api_key=api_key)
            
            # Prepare the prompt
            topics_list = [t.strip() for t in topics.replace('\n', ',').split(',') if t.strip()]
            topics_str = ", ".join(topics_list)
            
            prompt = f"""Generate {num_questions} questions and answers based on the following criteria:

- Total Marks: {marks}
- Topics: {topics_str}
- Bloom's Taxonomy Level: {bloom_level}

Requirements:
1. Strictly Generate {num_questions} questions ,each must carries {marks} marks questions.
2. Focus on the {bloom_level} level of Bloom's Taxonomy
3. Strictly Generate questions from provided topics {topics_str} or {syllabus_content}.
4. Each question should clearly indicate its mark value
5. Provide detailed, comprehensive answers for each question
6. Answer format should be in given {example_format} format only, genarate answer for {marks} only.
7. Generate new type of questions everytime that questions must be from  {syllabus_content}.

{f'Follow this format for questions and answers:{chr(10)}{example_format}' if example_format.strip() else ''}

Format each question as:
Q[number]. [Question text] ([marks] marks)
Answer: [Detailed answer]

Ensure answers are thorough and appropriate for the cognitive level specified.
Ensure that all the above points are strictly followed ,if not you are fired."""

            with st.spinner("🤖 Generating questions and answers..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert educator who creates high-quality exam questions and model answers based on Bloom's Taxonomy levels."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=3000
                )
                
                generated_content = response.choices[0].message.content
                
                # Display results
                st.success("✅ Questions and Answers Generated Successfully!")
                st.markdown("---")
                
                # Display in a nice formatted box
                st.markdown("### 📋 Generated Questions & Answers")
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;">
                {generated_content.replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
                
                # Copy to clipboard section
                st.markdown("---")
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    st.text_area(
                        "Copy the content below:",
                        value=generated_content,
                        height=300,
                        key="output_text"
                    )
                
                with col_b:
                    st.markdown("### 📋 Actions")
                    if st.button("📄 Copy All", use_container_width=True):
                        st.code(generated_content, language="text")
                        st.info("👆 Select all text above and copy (Ctrl+C / Cmd+C)")
                    
                    # Download option
                    st.download_button(
                        label="💾 Download as Text",
                        data=generated_content,
                        file_name="questions_and_answers.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Please check your API key and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>💡 Tip: Make sure your OpenAI API key has sufficient credits and proper permissions.</p>
</div>
""", unsafe_allow_html=True)