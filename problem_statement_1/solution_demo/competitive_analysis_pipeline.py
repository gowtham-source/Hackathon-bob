"""
Multi-Agent Competitive Analysis Pipeline using Gemini API
Uses google-genai SDK with the latest Client() pattern and gemini-3.1-flash-lite model

This pipeline implements three specialized agents:
1. Scout Agent - Searches and summarizes competitors
2. Analyst Agent - Compares top 3 competitors across pricing, features, and target audience
3. Reporter Agent - Compiles everything into a clean markdown brief
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Initialize Gemini client using the new Client() pattern
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Use gemini-3.1-flash-lite as specified
MODEL_NAME = "gemini-3.1-flash-lite"


def scout_agent(product_name: str) -> str:
    """
    Scout Agent: Searches and summarizes competitors in the product space
    
    Args:
        product_name: Name of the product to analyze
        
    Returns:
        Summary of competitors in the space
    """
    print(f"\n[Scout Agent] Researching competitors for '{product_name}'...")
    
    prompt = f"""You are a market research scout. Your task is to identify and summarize the main competitors for {product_name}.

Please provide:
1. A brief description of what {product_name} is and what market it operates in
2. List 5-7 main competitors in this space
3. A one-sentence description of each competitor

Be concise and factual. Focus on direct competitors that offer similar functionality."""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    
    result = response.text
    print(f"[Scout Agent] Research completed. Found competitors in the {product_name} space.")
    return result


def analyst_agent(product_name: str, scout_report: str) -> str:
    """
    Analyst Agent: Picks top 3 competitors and compares them in detail
    
    Args:
        product_name: Name of the product to analyze
        scout_report: Output from the scout agent
        
    Returns:
        Detailed comparison of top 3 competitors
    """
    print(f"\n[Analyst Agent] Analyzing top competitors...")
    
    prompt = f"""You are a competitive analyst. Based on the following scout report about {product_name} and its competitors, perform a detailed analysis.

SCOUT REPORT:
{scout_report}

Your task:
1. Select the TOP 3 most significant competitors from the scout report
2. For each competitor, provide a detailed comparison covering:
   - Pricing (tiers, costs, free options)
   - Key Features (what makes them unique)
   - Target Audience (who they serve best)
3. Create a comparison table or structured format

Be specific with pricing details and feature comparisons. Use actual information where possible."""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    
    result = response.text
    print(f"[Analyst Agent] Comparison completed for top 3 competitors.")
    return result


def reporter_agent(product_name: str, scout_report: str, analyst_report: str) -> str:
    """
    Reporter Agent: Compiles everything into a clean markdown brief
    
    Args:
        product_name: Name of the product to analyze
        scout_report: Output from the scout agent
        analyst_report: Output from the analyst agent
        
    Returns:
        Final markdown report
    """
    print(f"\n[Reporter Agent] Compiling final report...")
    
    prompt = f"""You are a professional business reporter. Compile a comprehensive competitive analysis brief for {product_name} based on the research below.

SCOUT REPORT:
{scout_report}

ANALYST REPORT:
{analyst_report}

Create a well-structured markdown document with:
1. Executive Summary (2-3 sentences)
2. Market Overview (what space {product_name} operates in)
3. Competitive Landscape (brief overview of all competitors mentioned)
4. Top 3 Competitors Deep Dive (detailed comparison from analyst report)
5. Key Takeaways (3-5 bullet points)

Use proper markdown formatting with headers, tables, bullet points, and bold text where appropriate.
Make it professional, concise, and actionable."""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    
    result = response.text
    print(f"[Reporter Agent] Final report completed.")
    return result


def run_competitive_analysis_pipeline(product_name: str) -> str:
    """
    Main pipeline orchestrator that runs all three agents sequentially
    
    Each agent calls the Gemini API independently and passes context forward:
    - Scout Agent identifies competitors
    - Analyst Agent receives scout report and performs detailed comparison
    - Reporter Agent receives both reports and creates final markdown brief
    
    Args:
        product_name: Name of the product to analyze
        
    Returns:
        Final markdown report
    """
    print(f"\n{'='*60}")
    print(f"Starting Competitive Analysis Pipeline for: {product_name}")
    print(f"Model: {MODEL_NAME}")
    print(f"{'='*60}")
    
    # Step 1: Scout Agent - Independent API call
    scout_report = scout_agent(product_name)
    
    # Step 2: Analyst Agent - Independent API call with scout context
    analyst_report = analyst_agent(product_name, scout_report)
    
    # Step 3: Reporter Agent - Independent API call with all context
    final_report = reporter_agent(product_name, scout_report, analyst_report)
    
    print(f"\n{'='*60}")
    print(f"Pipeline Complete!")
    print(f"{'='*60}\n")
    
    return final_report


def save_report(product_name: str, report: str, output_dir: str = "problem_statement_1/solution_demo"):
    """
    Save the report to a markdown file
    
    Args:
        product_name: Name of the product analyzed
        report: The markdown report content
        output_dir: Directory to save the report in
    """
    filename = f"{product_name.lower().replace(' ', '_')}_competitive_analysis.md"
    filepath = os.path.join(output_dir, filename)
    
    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report saved to: {filepath}")


if __name__ == "__main__":
    # Test the pipeline with "Notion" as requested
    product = "Notion"
    
    try:
        # Run the pipeline
        final_report = run_competitive_analysis_pipeline(product)
        
        # Display the final report
        print("\n" + "="*60)
        print("FINAL REPORT")
        print("="*60 + "\n")
        print(final_report)
        
        # Save to file
        save_report(product, final_report)
        
    except Exception as e:
        print(f"\n[ERROR] Error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

# Made with Bob
