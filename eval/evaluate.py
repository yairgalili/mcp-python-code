#!/usr/bin/env python3
"""
Comprehensive evaluation script for question-answer pairs using API endpoint.
Processes folders containing numbered .q.md and .a.md files and generates detailed quality reports.
"""

import asyncio
import os
import re
from fastmcp import Client
import requests
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time
import statistics
from datetime import datetime
import difflib
from collections import Counter
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from rouge_score import rouge_scorer
import textstat
import Levenshtein

# from app.main import mcp

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class QAEvaluator:
    def __init__(self, api_url: str = "http://localhost:8080/mcp", repo_path: str = ""):
        self.api_url = api_url
        self.repo_path = repo_path
        self.results = []
        self.response_times = []
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        self.stop_words = set(stopwords.words('english'))
        # self.client = asyncio.run(self.client)
    
    def load_qa_pairs(self, folder_path: str) -> List[Tuple[str, str, str]]:
        """Load question-answer pairs from folder."""
        qa_pairs = []
        folder = Path(folder_path)
        
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        question_files = sorted(folder.glob("*.q.md"))
        
        for q_file in question_files:
            match = re.match(r'(\d+)\.q\.md', q_file.name)
            if not match:
                print(f"Warning: Skipping malformed question file: {q_file.name}")
                continue
            
            number = match.group(1)
            a_file = folder / f"{number}.a.md"
            
            if not a_file.exists():
                print(f"Warning: No answer file found for {q_file.name}")
                continue
            
            try:
                with open(q_file, 'r', encoding='utf-8') as f:
                    question = f.read().strip()
                with open(a_file, 'r', encoding='utf-8') as f:
                    answer = f.read().strip()
                
                qa_pairs.append((q_file.name, question, answer))
            except Exception as e:
                print(f"Error reading files {q_file.name}/{a_file.name}: {e}")
                continue
        
        return qa_pairs
    
    async def query_api(self, question: str) -> Tuple[Optional[str], float, int]:
        """Query API and return prediction, response time."""
        try:
            payload = {"request": {"repo_path": self.repo_path, "question": question}}
            start_time = time.time()

            async with Client(self.api_url) as client:
            # async with Client(mcp) as client:
                # Connect via in-memory transport
                result = await client.call_tool("ask_question", payload)
            # response = requests.post(self.api_url, json=payload, timeout=36000)
            response_time = time.time() - start_time
            pred = json.loads(result.content[0].text)["answer"]
            return pred, response_time
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time if 'start_time' in locals() else 0
            return None, response_time
        except json.JSONDecodeError as e:
            return None, response_time if 'response' in locals() else 0
    
    def calculate_bleu_score(self, reference: str, hypothesis: str) -> float:
        """Calculate BLEU score between reference and hypothesis."""
        if not reference or not hypothesis:
            return 0.0
        
        ref_tokens = word_tokenize(reference.lower())
        hyp_tokens = word_tokenize(hypothesis.lower())
        
        smoothing = SmoothingFunction().method1
        return sentence_bleu([ref_tokens], hyp_tokens, smoothing_function=smoothing)
    
    def calculate_rouge_scores(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """Calculate ROUGE scores."""
        if not reference or not hypothesis:
            return {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}
        
        scores = self.rouge_scorer.score(reference, hypothesis)
        return {
            'rouge1': scores['rouge1'].fmeasure,
            'rouge2': scores['rouge2'].fmeasure,
            'rougeL': scores['rougeL'].fmeasure
        }
    
    def calculate_semantic_similarity(self, reference: str, hypothesis: str) -> float:
        """Calculate semantic similarity using word overlap."""
        if not reference or not hypothesis:
            return 0.0
        
        ref_words = set(word_tokenize(reference.lower())) - self.stop_words
        hyp_words = set(word_tokenize(hypothesis.lower())) - self.stop_words
        
        if not ref_words and not hyp_words:
            return 1.0
        if not ref_words or not hyp_words:
            return 0.0
        
        intersection = ref_words.intersection(hyp_words)
        union = ref_words.union(hyp_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def calculate_edit_distance_similarity(self, reference: str, hypothesis: str) -> float:
        """Calculate normalized edit distance similarity."""
        if not reference and not hypothesis:
            return 1.0
        if not reference or not hypothesis:
            return 0.0
        
        distance = Levenshtein.distance(reference, hypothesis)
        max_len = max(len(reference), len(hypothesis))
        return 1 - (distance / max_len) if max_len > 0 else 1.0
    
    def calculate_length_metrics(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """Calculate length-based metrics."""
        ref_len = len(reference.split()) if reference else 0
        hyp_len = len(hypothesis.split()) if hypothesis else 0
        
        length_ratio = hyp_len / ref_len if ref_len > 0 else 0
        length_diff = abs(hyp_len - ref_len)
        
        return {
            'length_ratio': length_ratio,
            'length_difference': length_diff,
            'ref_length': ref_len,
            'hyp_length': hyp_len
        }
    
    def calculate_readability_metrics(self, text: str) -> Dict[str, float]:
        """Calculate readability metrics for the generated text."""
        if not text:
            return {'flesch_reading_ease': 0, 'flesch_kincaid_grade': 0, 'gunning_fog': 0}
        
        return {
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            'gunning_fog': textstat.gunning_fog(text)
        }
    
    def analyze_content_coverage(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """Analyze how well the hypothesis covers the reference content."""
        if not reference or not hypothesis:
            return {'concept_coverage': 0.0, 'key_phrase_coverage': 0.0}
        
        # Extract key phrases (sequences of 2-3 words)
        ref_words = word_tokenize(reference.lower())
        hyp_words = word_tokenize(hypothesis.lower())
        
        ref_bigrams = set(zip(ref_words[:-1], ref_words[1:]))
        hyp_bigrams = set(zip(hyp_words[:-1], hyp_words[1:]))
        
        ref_trigrams = set(zip(ref_words[:-2], ref_words[1:-1], ref_words[2:]))
        hyp_trigrams = set(zip(hyp_words[:-2], hyp_words[1:-1], hyp_words[2:]))
        
        bigram_coverage = len(ref_bigrams.intersection(hyp_bigrams)) / len(ref_bigrams) if ref_bigrams else 0
        trigram_coverage = len(ref_trigrams.intersection(hyp_trigrams)) / len(ref_trigrams) if ref_trigrams else 0
        
        return {
            'concept_coverage': (bigram_coverage + trigram_coverage) / 2,
            'key_phrase_coverage': bigram_coverage
        }
    
    async def evaluate_pair(self, question_file: str, question: str, expected_answer: str) -> Dict:
        """Evaluate a single question-answer pair with comprehensive metrics."""
        print(f"Evaluating {question_file}...")
        
        predicted_answer, response_time = await self.query_api(question)
        self.response_times.append(response_time)
        
        if predicted_answer is None:
            return {
                "question_file": question_file,
                "question": question,
                "expected_answer": expected_answer,
                "predicted_answer": None,
                "success": False,
                "error": "API call failed",
                "response_time": response_time,
                "metrics": {}
            }
        
        # Calculate all metrics
        bleu_score = self.calculate_bleu_score(expected_answer, predicted_answer)
        rouge_scores = self.calculate_rouge_scores(expected_answer, predicted_answer)
        semantic_sim = self.calculate_semantic_similarity(expected_answer, predicted_answer)
        edit_sim = self.calculate_edit_distance_similarity(expected_answer, predicted_answer)
        length_metrics = self.calculate_length_metrics(expected_answer, predicted_answer)
        readability = self.calculate_readability_metrics(predicted_answer)
        coverage = self.analyze_content_coverage(expected_answer, predicted_answer)
        
        metrics = {
            "bleu_score": bleu_score,
            "rouge_scores": rouge_scores,
            "semantic_similarity": semantic_sim,
            "edit_distance_similarity": edit_sim,
            "length_metrics": length_metrics,
            "readability": readability,
            "content_coverage": coverage,
            "response_time": response_time
        }
        
        result = {
            "question_file": question_file,
            "question": question,
            "expected_answer": expected_answer,
            "predicted_answer": predicted_answer,
            "success": True,
            "error": None,
            "response_time": response_time,
            "metrics": metrics
        }
        
        return result
    
    async def run_evaluation(self, folder_path: str) -> List[Dict]:
        """Run comprehensive evaluation on all Q&A pairs."""
        print(f"Loading Q&A pairs from: {folder_path}")
        qa_pairs = self.load_qa_pairs(folder_path)
        
        if not qa_pairs:
            print("No valid Q&A pairs found!")
            return []
        
        print(f"Found {len(qa_pairs)} Q&A pairs")
        
        results = []
        start_time = time.time()
        
        for i, (question_file, question, answer) in enumerate(qa_pairs, 1):
            print(f"\n[{i}/{len(qa_pairs)}] Processing {question_file}")
            
            result = await self.evaluate_pair(question_file, question, answer)
            results.append(result)
        
        total_time = time.time() - start_time
        print(f"\nTotal evaluation time: {total_time:.2f} seconds")
        
        self.results = results
        return results
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate a comprehensive quality report."""
        if not self.results:
            return {}
        
        successful_results = [r for r in self.results]
        total_count = len(self.results)
        success_count = len(successful_results)
        
        # Performance metrics
        avg_response_time = statistics.mean(self.response_times) if self.response_times else 0
        success_rate = success_count / total_count if total_count > 0 else 0
        
        if not successful_results:
            return {
                "summary": {
                    "total_questions": total_count,
                    "successful_evaluations": success_count,
                    "success_rate": success_rate,
                    "average_response_time": avg_response_time
                },
                "quality_metrics": {},
                "performance_analysis": {},
                "recommendations": ["All evaluations failed - check API connectivity and server status"]
            }
        
        # Extract metrics from successful results
        bleu_scores = [r['metrics']['bleu_score'] for r in successful_results]
        rouge1_scores = [r['metrics']['rouge_scores']['rouge1'] for r in successful_results]
        rouge2_scores = [r['metrics']['rouge_scores']['rouge2'] for r in successful_results]
        rougeL_scores = [r['metrics']['rouge_scores']['rougeL'] for r in successful_results]
        semantic_sims = [r['metrics']['semantic_similarity'] for r in successful_results]
        edit_sims = [r['metrics']['edit_distance_similarity'] for r in successful_results]
        length_ratios = [r['metrics']['length_metrics']['length_ratio'] for r in successful_results]
        
        # Quality metrics analysis
        quality_metrics = {
            "bleu_score": {
                "mean": statistics.mean(bleu_scores),
                "median": statistics.median(bleu_scores),
                "std": statistics.stdev(bleu_scores) if len(bleu_scores) > 1 else 0,
                "min": min(bleu_scores),
                "max": max(bleu_scores)
            },
            "rouge_scores": {
                "rouge1": {
                    "mean": statistics.mean(rouge1_scores),
                    "median": statistics.median(rouge1_scores),
                    "std": statistics.stdev(rouge1_scores) if len(rouge1_scores) > 1 else 0
                },
                "rouge2": {
                    "mean": statistics.mean(rouge2_scores),
                    "median": statistics.median(rouge2_scores),
                    "std": statistics.stdev(rouge2_scores) if len(rouge2_scores) > 1 else 0
                },
                "rougeL": {
                    "mean": statistics.mean(rougeL_scores),
                    "median": statistics.median(rougeL_scores),
                    "std": statistics.stdev(rougeL_scores) if len(rougeL_scores) > 1 else 0
                }
            },
            "semantic_similarity": {
                "mean": statistics.mean(semantic_sims),
                "median": statistics.median(semantic_sims),
                "std": statistics.stdev(semantic_sims) if len(semantic_sims) > 1 else 0
            },
            "edit_distance_similarity": {
                "mean": statistics.mean(edit_sims),
                "median": statistics.median(edit_sims),
                "std": statistics.stdev(edit_sims) if len(edit_sims) > 1 else 0
            },
            "length_consistency": {
                "mean_ratio": statistics.mean(length_ratios),
                "median_ratio": statistics.median(length_ratios),
                "std_ratio": statistics.stdev(length_ratios) if len(length_ratios) > 1 else 0
            }
        }
        
        # Performance analysis
        response_times = [r['response_time'] for r in self.results]
        performance_analysis = {
            "response_time": {
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times),
                "std": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "min": min(response_times),
                "max": max(response_times),
                "p95": sorted(response_times)[int(0.95 * len(response_times))] if response_times else 0
            },
            "throughput": {
                "questions_per_second": success_count / sum(response_times) if sum(response_times) > 0 else 0
            },
            "reliability": {
                "success_rate": success_rate,
                "error_rate": 1 - success_rate,
                "total_errors": total_count - success_count
            }
        }
        
        # Generate recommendations
        recommendations = self.generate_recommendations(quality_metrics, performance_analysis, success_rate)
        
        # Overall quality score (0-100)
        overall_score = self.calculate_overall_score(quality_metrics, performance_analysis, success_rate)
        
        return {
            "evaluation_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_questions": total_count,
                "successful_evaluations": success_count,
                "success_rate": success_rate,
                "average_response_time": avg_response_time,
                "overall_quality_score": overall_score
            },
            "quality_metrics": quality_metrics,
            "performance_analysis": performance_analysis,
            "recommendations": recommendations,
            "grade": self.assign_grade(overall_score)
        }
    
    def calculate_overall_score(self, quality_metrics: Dict, performance_analysis: Dict, success_rate: float) -> float:
        """Calculate an overall quality score (0-100)."""
        # Weighted scoring
        weights = {
            'content_quality': 0.4,  # BLEU, ROUGE, semantic similarity
            'performance': 0.3,      # Response time, success rate
            'consistency': 0.3       # Length consistency, edit distance
        }
        
        # Content quality (average of key metrics)
        content_scores = [
            quality_metrics['bleu_score']['mean'],
            quality_metrics['rouge_scores']['rouge1']['mean'],
            quality_metrics['rouge_scores']['rougeL']['mean'],
            quality_metrics['semantic_similarity']['mean']
        ]
        content_quality = statistics.mean(content_scores) * 100
        
        # Performance score (based on success rate and response time)
        perf_score = success_rate * 100
        if performance_analysis['response_time']['mean'] < 1.0:
            perf_score *= 1.0  # No penalty for fast responses
        elif performance_analysis['response_time']['mean'] < 3.0:
            perf_score *= 0.9  # Small penalty for medium responses
        else:
            perf_score *= 0.7  # Larger penalty for slow responses
        
        # Consistency score
        consistency_scores = [
            quality_metrics['edit_distance_similarity']['mean'],
            min(1.0, 1.0 / (1.0 + abs(quality_metrics['length_consistency']['mean_ratio'] - 1.0)))
        ]
        consistency_quality = statistics.mean(consistency_scores) * 100
        
        overall_score = (
            content_quality * weights['content_quality'] +
            perf_score * weights['performance'] +
            consistency_quality * weights['consistency']
        )
        
        return min(100.0, max(0.0, overall_score))
    
    def assign_grade(self, score: float) -> str:
        """Assign a letter grade based on the overall score."""
        if score >= 90: return "A"
        elif score >= 80: return "B"
        elif score >= 70: return "C"
        elif score >= 60: return "D"
        else: return "F"
    
    def generate_recommendations(self, quality_metrics: Dict, performance_analysis: Dict, success_rate: float) -> List[str]:
        """Generate actionable recommendations based on the evaluation results."""
        recommendations = []
        
        # Success rate recommendations
        if success_rate < 0.95:
            recommendations.append(f"LOW SUCCESS RATE ({success_rate:.2%}): Check API reliability and error handling")
        
        # Response time recommendations
        avg_time = performance_analysis['response_time']['mean']
        if avg_time > 5.0:
            recommendations.append(f"SLOW RESPONSE TIME ({avg_time:.2f}s): Consider optimizing server performance")
        elif avg_time > 2.0:
            recommendations.append(f"MODERATE RESPONSE TIME ({avg_time:.2f}s): Room for performance improvement")
        
        # Content quality recommendations
        bleu_mean = quality_metrics['bleu_score']['mean']
        if bleu_mean < 0.3:
            recommendations.append(f"LOW BLEU SCORE ({bleu_mean:.3f}): Generated answers may not match expected format")
        
        rouge1_mean = quality_metrics['rouge_scores']['rouge1']['mean']
        if rouge1_mean < 0.4:
            recommendations.append(f"LOW ROUGE-1 SCORE ({rouge1_mean:.3f}): Generated answers lack content overlap")
        
        semantic_mean = quality_metrics['semantic_similarity']['mean']
        if semantic_mean < 0.5:
            recommendations.append(f"LOW SEMANTIC SIMILARITY ({semantic_mean:.3f}): Answers may be semantically different")
        
        # Length consistency recommendations
        length_ratio = quality_metrics['length_consistency']['mean_ratio']
        if length_ratio < 0.5:
            recommendations.append("ANSWERS TOO SHORT: Generated answers are significantly shorter than expected")
        elif length_ratio > 2.0:
            recommendations.append("ANSWERS TOO LONG: Generated answers are significantly longer than expected")
        
        # Consistency recommendations
        edit_sim = quality_metrics['edit_distance_similarity']['mean']
        if edit_sim < 0.4:
            recommendations.append(f"LOW EDIT SIMILARITY ({edit_sim:.3f}): High text-level differences from expected answers")
        
        if not recommendations:
            recommendations.append("EXCELLENT PERFORMANCE: All metrics are within acceptable ranges")
        
        return recommendations
    
    def save_results(self, output_file: str):
        """Save detailed evaluation results to JSON file."""
        report = self.generate_comprehensive_report()
        
        output_data = {
            "report": report,
            "detailed_results": self.results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed results saved to: {output_file}")
    
    def print_summary_report(self):
        """Print a comprehensive summary report."""
        report = self.generate_comprehensive_report()
        
        if not report:
            print("No results to report.")
            return
        
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE SERVER QUALITY REPORT")
        print(f"{'='*80}")
        print(f"Evaluation Date: {report['evaluation_timestamp']}")
        print(f"Overall Grade: {report['grade']} ({report['summary']['overall_quality_score']:.1f}/100)")
        
        print(f"\n{'SUMMARY':-<80}")
        summary = report['summary']
        print(f"Total Questions: {summary['total_questions']}")
        print(f"Successful Evaluations: {summary['successful_evaluations']}")
        print(f"Success Rate: {summary['success_rate']:.2%}")
        print(f"Average Response Time: {summary['average_response_time']:.3f}s")
        
        print(f"\n{'QUALITY METRICS':-<80}")
        quality = report['quality_metrics']
        
        print(f"BLEU Score: {quality['bleu_score']['mean']:.3f} ± {quality['bleu_score']['std']:.3f}")
        print(f"ROUGE-1: {quality['rouge_scores']['rouge1']['mean']:.3f} ± {quality['rouge_scores']['rouge1']['std']:.3f}")
        print(f"ROUGE-2: {quality['rouge_scores']['rouge2']['mean']:.3f} ± {quality['rouge_scores']['rouge2']['std']:.3f}")
        print(f"ROUGE-L: {quality['rouge_scores']['rougeL']['mean']:.3f} ± {quality['rouge_scores']['rougeL']['std']:.3f}")
        print(f"Semantic Similarity: {quality['semantic_similarity']['mean']:.3f} ± {quality['semantic_similarity']['std']:.3f}")
        print(f"Edit Distance Similarity: {quality['edit_distance_similarity']['mean']:.3f} ± {quality['edit_distance_similarity']['std']:.3f}")
        print(f"Length Ratio: {quality['length_consistency']['mean_ratio']:.3f} ± {quality['length_consistency']['std_ratio']:.3f}")
        
        print(f"\n{'PERFORMANCE ANALYSIS':-<80}")
        perf = report['performance_analysis']
        rt = perf['response_time']
        print(f"Response Time - Mean: {rt['mean']:.3f}s, Median: {rt['median']:.3f}s, P95: {rt['p95']:.3f}s")
        print(f"Throughput: {perf['throughput']['questions_per_second']:.2f} questions/second")
        print(f"Error Rate: {perf['reliability']['error_rate']:.2%}")
        
        print(f"\n{'RECOMMENDATIONS':-<80}")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print(f"\n{'='*80}")

async def main():
    parser = argparse.ArgumentParser(description="Comprehensive Q&A evaluation with detailed quality reporting")
    parser.add_argument("folder", help="Path to folder containing .q.md and .a.md files")
    parser.add_argument("--api-url", default="http://localhost:8080/mcp", 
                       help="API endpoint URL (default: http://localhost:8080/mcp)")
    parser.add_argument("--repo-path", default="./grip-repo", 
                       help="Repository path to send to API")
    parser.add_argument("--output", "-o", default="evaluation_report.json",
                       help="Output file for results (default: evaluation_report.json)")
    
    args = parser.parse_args()
    
    evaluator = QAEvaluator(api_url=args.api_url, repo_path=args.repo_path)
    
    try:
        results = await evaluator.run_evaluation(args.folder)
        
        if results:
            evaluator.save_results(args.output)
            evaluator.print_summary_report()
        
    except KeyboardInterrupt:
        print("\nEvaluation interrupted by user.")
    except Exception as e:
        print(f"Error during evaluation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())