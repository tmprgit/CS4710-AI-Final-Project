#!/usr/bin/env python3
import os
import sys
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(base_dir))

from engine import CourseRecommender, StudentProfile
from catalog import load_courses
from scheduler import find_similar_course_pairs, build_schedules

app = Flask(__name__, static_folder=os.path.join(base_dir, 'static'), static_url_path='')
CORS(app)

COURSES = load_courses()
rec = CourseRecommender()
rec.build_index(COURSES)

def fmt_section(sec):
    parts = []
    for m in sec.get('meetings', []):
        days = '/'.join(d[:2] for d in m.get('days', [])) or 'TBA'
        start, end = m.get('start'), m.get('end')
        time = f"{start}–{end}" if start and end else 'TBA'
        parts.append(f"{days} {time}")
    return '; '.join(parts) or 'TBA'


@app.route('/')
def index():
    return send_from_directory(os.path.join(base_dir, 'static'), 'index.html')


@app.route('/api/courses')
def api_courses():
    return jsonify([{'id': c['id'], 'title': c['title'], 'desc': c['description'], 'prereqs': c.get('prereqs', [])} for c in COURSES])


@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    data = request.json
    profile = StudentProfile.from_dict(data)
    results = rec.query(data['query'], profile, top_k=5)
    return jsonify([{
        'id': r.course['id'],
        'title': r.course['title'],
        'score': f"{r.final_score:.0%}",
        'desc': r.course['description'],
        'prereqs': r.course.get('prereqs', [])
    } for r in results])


@app.route('/api/schedule', methods=['POST'])
def api_schedule():
    data = request.json
    profile = StudentProfile.from_dict(data)
    results = rec.query(data['query'], profile, top_k=20)

    similar_pairs = find_similar_course_pairs([r.course for r in results], rec.bi)

    schedules = build_schedules(results, None, similar_pairs,
                                student_year=profile.year,
                                target_credits=int(data.get('target_credits', 15)),
                                top_n=5)

    return jsonify([{
        'score': round(s.total_score, 3),
        'relevance': round(s.relevance_score, 3),
        'penalty': round(s.penalty, 3),
        'courses': [{
            'id': slot.course['id'],
            'title': slot.course['title'],
            'credits': slot.course.get('credits', ''),
            'recommendation_score': f"{slot.recommendation_score:.0%}",
            'section': slot.section.get('section', ''),
            'time': fmt_section(slot.section),
            'instructor': slot.section.get('instructor', 'TBA'),
        } for slot in s.courses],
    } for s in schedules])


if __name__ == '__main__':
    app.run(debug=False, port=5000)
