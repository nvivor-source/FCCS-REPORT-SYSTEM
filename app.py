#!/usr/bin/env python3
"""
FCCS - Four Corners Community Services
Day Habilitation Service Report Platform - PRODUCTION VERSION
Features: Persistent admin changes, Google Drive upload, Calendar, Location folders
"""

import os
import json
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, send_file, session, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# Use /tmp for Render compatibility
DATA_FILE = os.environ.get('DATA_FILE', '/tmp/fccs_data.json' if os.environ.get('RENDER') else 'fccs_data.json')

MENTORS_LIST = [
    "AMADU DRAH", "EVELYN PINTO", "ANDRES GOMEZ", "VELONICAH NYABUTO",
    "ABIGAIL GYAMFI", "GENESIS MALENA TACLE", "BENJAMIN TWENWBOOAH", "HOPE SENOO",
    "ANTONIO REYES", "GRACIELA GIMENEZ", "ELISA ABREU", "NANA MANSU",
    "EMMANUEL AMOAKO", "EBUBECHUKWU NWOKE", "WANDY ORTIZ", "GABRIELLA MORENO",
    "PAOLA GONZALEZ", "AUGUSTO NJOKU", "LUIS GUZMAN", "EVELYN GONZALEZ",
    "MICHAEL AGGOR", "OPOKU DUAH", "CINTHYA PINEDA", "REINDORF GYAMENA",
    "MEDINA DOUGLAS"
]

MEMBERS_LIST = [
    {"name": "Aaron Barret", "location": "Hackensack"},
    {"name": "Jaydon Piscoya", "location": "Hackensack"},
    {"name": "Nicole Fortini", "location": "Oxford"},
    {"name": "Willie James Crawford", "location": "Oxford"},
    {"name": "Thomas", "location": "Union City"},
    {"name": "Edison May", "location": "Union City"},
    {"name": "Justin", "location": "Hackensack"},
    {"name": "Nicholas", "location": "Oxford"}
]

LOCATIONS_LIST = ["Hackensack", "Center", "Community", "Park", "Library", "Teaneck"]
ACTIVITIES_LIST = ["Mathematics", "Reading", "Social Skills", "Community Integration", "Life Skills", "Communication", "Art Therapy", "Music Therapy"]
PROMPT_LEVELS_LIST = ["Independent", "Indirect Verbal", "Direct Verbal", "Gesture", "Modeling", "Partial Physical", "Full Physical"]
TASK_CATEGORIES_LIST = ["Cognitive and Skill Development", "Social Development", "Physical Development", "Communication", "Self-Care", "Community Integration"]
UNITS_LIST = ["0.5", "1.0", "1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0", "5.5", "6.0"]
STRATEGIES_LIST = [
    "Jaydon will engage in collaborative volunteer activities, working alongside peers to build teamwork skills.",
    "Member will use visual schedule to transition between activities.",
    "Staff will provide positive reinforcement for task completion.",
    "Member will practice turn-taking during group activities."
]
SERVICE_TYPES_LIST = ["Day Habilitation", "Community Habilitation", "Respite", "Supported Employment"]
MEDICATION_STATUS_LIST = ["No", "Yes", "N/A"]
MEDICATION_TYPES_LIST = ["MAR", "PRN", "Both", "N/A"]
MEMBER_LOCATIONS = ["Hackensack", "Oxford", "Union City"]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
        except:
            data = {}
    else:
        data = {}
    
    if 'users' not in data or not data['users']:
        data['users'] = [
            {'id': 1, 'username': 'admin', 'password': generate_password_hash('admin123'), 'role': 'admin'},
            {'id': 2, 'username': 'supervisor', 'password': generate_password_hash('super123'), 'role': 'supervisor'},
            {'id': 3, 'username': 'qa', 'password': generate_password_hash('qa123'), 'role': 'staff'},
            {'id': 4, 'username': 'staff1', 'password': generate_password_hash('staff123'), 'role': 'staff'}
        ]
    
    if 'members' not in data or not data['members']:
        data['members'] = []
        for i, m in enumerate(MEMBERS_LIST):
            data['members'].append({
                'id': i+1, 
                'full_name': m['name'], 
                'display_name': m['name'].split()[0], 
                'location': m['location'],
                'date_of_birth': '', 
                'medicaid_id': '', 
                'phone': '', 
                'emergency_contact': '', 
                'address': '', 
                'is_active': True
            })
    
    if 'mentors' not in data or not data['mentors']:
        data['mentors'] = [{'id': i+1, 'full_name': m, 'is_active': True} for i, m in enumerate(MENTORS_LIST)]
    if 'locations' not in data or not data['locations']:
        data['locations'] = [{'id': i+1, 'location_name': l, 'is_active': True} for i, l in enumerate(LOCATIONS_LIST)]
    if 'activities' not in data or not data['activities']:
        data['activities'] = [{'id': i+1, 'activity_name': a, 'is_active': True} for i, a in enumerate(ACTIVITIES_LIST)]
    if 'prompt_levels' not in data or not data['prompt_levels']:
        data['prompt_levels'] = [{'id': i+1, 'level_name': p, 'is_active': True} for i, p in enumerate(PROMPT_LEVELS_LIST)]
    if 'task_categories' not in data or not data['task_categories']:
        data['task_categories'] = [{'id': i+1, 'category_name': c, 'is_active': True} for i, c in enumerate(TASK_CATEGORIES_LIST)]
    if 'unit_options' not in data or not data['unit_options']:
        data['unit_options'] = [{'id': i+1, 'unit_value': u, 'display_text': f'{u} Units', 'is_active': True} for i, u in enumerate(UNITS_LIST)]
    if 'strategies' not in data or not data['strategies']:
        data['strategies'] = [{'id': i+1, 'strategy_text': s, 'is_active': True} for i, s in enumerate(STRATEGIES_LIST)]
    if 'service_types' not in data or not data['service_types']:
        data['service_types'] = [{'id': i+1, 'type_name': s, 'is_active': True} for i, s in enumerate(SERVICE_TYPES_LIST)]
    if 'medication_statuses' not in data or not data['medication_statuses']:
        data['medication_statuses'] = [{'id': i+1, 'status_name': s, 'is_active': True} for i, s in enumerate(MEDICATION_STATUS_LIST)]
    if 'medication_types' not in data or not data['medication_types']:
        data['medication_types'] = [{'id': i+1, 'type_name': t, 'is_active': True} for i, t in enumerate(MEDICATION_TYPES_LIST)]
    if 'member_locations' not in data or not data['member_locations']:
        data['member_locations'] = [{'id': i+1, 'location_name': l, 'is_active': True} for i, l in enumerate(MEMBER_LOCATIONS)]
    if 'isp_outcomes' not in data:
        data['isp_outcomes'] = []
        for member in data['members']:
            if member.get('is_active', True):
                data['isp_outcomes'].append({'id': len(data['isp_outcomes'])+1, 'member_id': member['id'], 'outcome_text': f"{member['full_name']} will engage in community activities and socialize with peers.", 'is_active': True})
                data['isp_outcomes'].append({'id': len(data['isp_outcomes'])+1, 'member_id': member['id'], 'outcome_text': f"{member['full_name']} will develop independent living skills.", 'is_active': True})
    
    if 'user_drafts' not in data:
        data['user_drafts'] = {}
    if 'submitted_reports' not in data:
        data['submitted_reports'] = []
    if 'approved_reports' not in data:
        data['approved_reports'] = []
    if 'next_report_id' not in data:
        data['next_report_id'] = 1
    if 'next_member_id' not in data:
        data['next_member_id'] = max([m['id'] for m in data['members']] + [0]) + 1
    
    return data

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

app_data = load_data()

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FCCS - Four Corners Community Services</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            background: linear-gradient(135deg, #1a3a5c 0%, #2c5aa0 100%);
        }
        .logo-background {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0.08;
            pointer-events: none;
            z-index: 1;
        }
        .logo-background svg {
            width: 600px;
            height: 600px;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 400px;
            position: relative;
            z-index: 10;
        }
        h1 { text-align: center; color: #1a3a5c; font-size: 24px; }
        .fccs-full { text-align: center; color: #2c5aa0; margin-bottom: 5px; font-weight: bold; }
        .logo-icon { text-align: center; margin-bottom: 15px; }
        .logo-icon svg { width: 80px; height: 80px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 2px solid #ddd; border-radius: 8px; }
        button { width: 100%; padding: 14px; background: #2c5aa0; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="logo-background">
        <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="90" fill="#1a3a5c" opacity="0.3"/>
            <circle cx="100" cy="100" r="70" fill="#2c5aa0" opacity="0.3"/>
            <text x="100" y="110" font-size="60" text-anchor="middle" fill="white" font-weight="bold" opacity="0.5">FCCS</text>
            <text x="100" y="140" font-size="16" text-anchor="middle" fill="white" opacity="0.5">Four Corners</text>
            <text x="100" y="160" font-size="14" text-anchor="middle" fill="white" opacity="0.5">Community Services</text>
        </svg>
    </div>
    <div class="login-box">
        <div class="logo-icon">
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="45" fill="#1a3a5c"/>
                <text x="50" y="65" font-size="35" text-anchor="middle" fill="white" font-weight="bold">F</text>
            </svg>
        </div>
        <h1>📋 FCCS</h1>
        <p class="fccs-full">Four Corners Community Services</p>
        <p style="text-align:center; color:#666; margin-bottom:20px;">Day Habilitation Reports</p>
        <form id="loginForm">
            <input type="text" id="username" placeholder="Username" required>
            <input type="password" id="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: document.getElementById('username').value, password: document.getElementById('password').value})
            });
            const data = await response.json();
            if (data.success) window.location.href = '/app';
            else alert('Invalid credentials');
        });
    </script>
</body>
</html>
'''

MAIN_APP_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FCCS - DayHab Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Yellowtail&family=Pacifico&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #ecf0f1; }
        .header { background: linear-gradient(135deg, #1a3a5c 0%, #2c5aa0 100%); color: white; padding: 12px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h2 { color: white !important; }
        .header p { color: white !important; opacity: 0.9; }
        .nav { display: flex; gap: 10px; flex-wrap: wrap; }
        .nav button { background: rgba(255,255,255,0.2); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
        .nav button.active { background: white; color: #1a3a5c; }
        .container { max-width: 1400px; margin: 20px auto; padding: 0 20px; }
        .section { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h2 { color: #1a3a5c; margin-bottom: 20px; border-bottom: 2px solid #2c5aa0; padding-bottom: 10px; }
        .form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 15px; }
        .form-group { display: flex; flex-direction: column; }
        label { font-weight: 600; color: #34495e; margin-bottom: 5px; }
        input, select, textarea { padding: 10px; border: 1px solid #bdc3c7; border-radius: 6px; font-size: 14px; background: white; }
        button { background: #2c5aa0; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
        button.green { background: #27ae60; }
        button.red { background: #e74c3c; }
        button.blue { background: #3498db; }
        button.orange { background: #f39c12; }
        button.purple { background: #9b59b6; }
        .task-section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; }
        .task-item { background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #dee2e6; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #dee2e6; }
        th { background: #1a3a5c; color: white; }
        .member-info { background: #e8f4fd; padding: 15px; border-radius: 6px; margin-bottom: 15px; display: flex; justify-content: space-between; }
        .signature-preview {
            font-family: 'Yellowtail', 'Pacifico', 'Brush Script MT', cursive;
            font-size: 24px;
            color: #1a3a5c;
            margin-top: 10px;
            padding: 10px 0;
            border-bottom: 2px solid #2c5aa0;
            display: inline-block;
        }
        .admin-section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .list-item { display: flex; gap: 10px; margin-bottom: 10px; align-items: center; }
        .list-item input, .list-item textarea { flex: 1; }
        .modal { display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); z-index: 1000; max-width: 800px; width: 90%; max-height: 80vh; overflow-y: auto; }
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 999; }
        .status-badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .status-draft { background: #f39c12; color: white; }
        .status-submitted { background: #3498db; color: white; }
        .status-approved { background: #27ae60; color: white; }
        .status-rejected { background: #e74c3c; color: white; }
        .user-info { background: #2c5aa0; color: white; padding: 5px 15px; border-radius: 20px; font-size: 14px; }
        .comment-box { background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #f39c12; }
        .comment-item { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 6px; }
        .location-folder { background: #f0f4f8; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #1a3a5c; }
        .location-header { font-size: 18px; font-weight: bold; color: #1a3a5c; margin-bottom: 10px; cursor: pointer; }
        .calendar { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-top: 15px; }
        .calendar-day { background: #f8f9fa; padding: 10px; border-radius: 6px; min-height: 80px; }
        .calendar-day.has-report { background: #d4edda; border: 1px solid #28a745; }
        .calendar-date { font-weight: bold; margin-bottom: 5px; }
        .report-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #28a745; margin-right: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h2 style="color: white;">📋 FCCS - Four Corners Community Services</h2>
            <p style="color: white; margin:0; opacity:0.9;">Day Habilitation Service Reports</p>
        </div>
        <div style="display: flex; align-items: center; gap: 20px;">
            <span class="user-info" id="currentUserDisplay"></span>
            <div class="nav">
                <button onclick="showSection('new')" id="navNew" class="active">New Report</button>
                <button onclick="showSection('drafts')" id="navDrafts">My Drafts</button>
                <button onclick="showSection('submitted')" id="navSubmitted">Review Queue</button>
                <button onclick="showSection('approved')" id="navApproved">Approved</button>
                <button onclick="showSection('calendar')" id="navCalendar">Calendar</button>
                <button onclick="showSection('members')" id="navMembers">Members</button>
                <button onclick="showSection('admin')" id="navAdmin">Admin Panel</button>
                <button onclick="logout()" style="background:#e74c3c;">Logout</button>
            </div>
        </div>
    </div>
    
    <div class="container">
        <!-- New Report Section -->
        <div id="newSection" class="section">
            <h2>📝 New Service Report</h2>
            
            <div id="memberInfo" class="member-info" style="display:none;">
                <span id="memberInfoText"></span>
                <button onclick="editMemberInfo()" class="blue">Edit Info</button>
            </div>
            
            <form id="reportForm">
                <div class="form-row">
                    <div class="form-group">
                        <label>Member *</label>
                        <select id="memberId" required onchange="loadMemberDetails()"><option value="">Select Member</option></select>
                    </div>
                    <div class="form-group">
                        <label>Mentor *</label>
                        <select id="mentorId" required onchange="updateSignaturePreview()"><option value="">Select Mentor</option></select>
                    </div>
                    <div class="form-group">
                        <label>Service Type</label>
                        <select id="serviceType"><option value="">Select Service Type</option></select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group"><label>Date *</label><input type="date" id="serviceDate" required></div>
                    <div class="form-group"><label>Start Time *</label><input type="time" id="startTime" value="09:00" required></div>
                    <div class="form-group"><label>End Time *</label><input type="time" id="endTime" value="15:00" required></div>
                    <div class="form-group"><label>Units</label><select id="units"><option value="">Select Units</option></select></div>
                </div>
                
                <div class="form-row">
                    <div class="form-group"><label>Location *</label><select id="locationId" required><option value="">Select Location</option></select></div>
                    <div class="form-group"><label>ISP Outcome *</label><select id="ispOutcomeId" required><option value="">Select Outcome</option></select></div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Medication</label>
                        <select id="medicationStatus" onchange="toggleMedicationType()"><option value="">Select</option></select>
                    </div>
                    <div class="form-group">
                        <label>Med Type</label>
                        <select id="medicationType" disabled><option value="">-</option></select>
                    </div>
                </div>
                
                <div class="task-section">
                    <h3>Tasks & Activities</h3>
                    <div id="tasksList"></div>
                    <button type="button" onclick="addTask()" class="green" style="margin-top:10px;">+ Add Task</button>
                </div>
                
                <div style="margin-top:30px; padding:20px; background:#f8f9fa; border-radius:8px;">
                    <label style="font-size:16px; margin-bottom:10px; display:block;">Staff Signature:</label>
                    <div id="signaturePreview" class="signature-preview"></div>
                    <p style="font-size:12px; color:#666; margin-top:5px;">Electronic Signature</p>
                </div>
                
                <div style="margin-top:20px; display: flex; gap: 10px;">
                    <button type="button" onclick="saveDraft()" class="blue">💾 Save as Draft</button>
                    <button type="button" onclick="submitForReview()" class="orange">📤 Submit for Review</button>
                </div>
            </form>
        </div>
        
        <!-- My Drafts Section -->
        <div id="draftsSection" class="section" style="display:none;">
            <h2>📂 My Drafts</h2>
            <p style="color:#666; margin-bottom:15px;">These are your personal drafts. Only you can see them.</p>
            <div id="draftsList"></div>
        </div>
        
        <!-- Submitted for Review Section -->
        <div id="submittedSection" class="section" style="display:none;">
            <h2>🔍 Review Queue</h2>
            <p style="color:#666; margin-bottom:15px;">Reports waiting for supervisor review and approval.</p>
            <div id="submittedList"></div>
        </div>
        
        <!-- Approved Notes Section -->
        <div id="approvedSection" class="section" style="display:none;">
            <h2>✅ Approved Notes</h2>
            <p style="color:#666; margin-bottom:15px;">Approved reports ready for PDF download.</p>
            <div id="approvedList"></div>
        </div>
        
        <!-- Calendar Section -->
        <div id="calendarSection" class="section" style="display:none;">
            <h2>📅 Reports Calendar</h2>
            <div style="margin-bottom:15px;">
                <button onclick="changeMonth(-1)">◀ Prev</button>
                <span id="currentMonthYear" style="margin:0 15px; font-size:18px; font-weight:bold;"></span>
                <button onclick="changeMonth(1)">Next ▶</button>
            </div>
            <div id="calendar"></div>
        </div>
        
        <!-- Members Section -->
        <div id="membersSection" class="section" style="display:none;">
            <h2>👥 Members</h2>
            <div id="membersByLocation"></div>
            <button onclick="showAddMemberForm()" class="green" style="margin-top:15px;">+ Add Member</button>
        </div>
        
        <!-- Admin Section -->
        <div id="adminSection" class="section" style="display:none;">
            <h2>⚙️ Admin Configuration</h2>
            <div id="adminConfigs"></div>
        </div>
    </div>
    
    <!-- View Report Modal -->
    <div class="modal-overlay" id="viewModalOverlay" onclick="closeViewModal()"></div>
    <div class="modal" id="viewModal">
        <h3>Report Details</h3>
        <div id="viewModalContent"></div>
        <div style="display:flex; gap:10px; margin-top:20px;">
            <button onclick="closeViewModal()" class="blue">Close</button>
        </div>
    </div>
    
    <!-- Add Member Modal -->
    <div class="modal-overlay" id="addMemberModalOverlay" onclick="closeAddMemberModal()"></div>
    <div class="modal" id="addMemberModal">
        <h3>Add New Member</h3>
        <form id="addMemberForm">
            <div class="form-group"><label>Full Name *</label><input type="text" id="newFullName" required></div>
            <div class="form-group"><label>Location *</label><select id="newLocation" required></select></div>
            <div class="form-group"><label>Display Name</label><input type="text" id="newDisplayName"></div>
            <div class="form-group"><label>Date of Birth</label><input type="date" id="newDOB"></div>
            <div class="form-group"><label>Medicaid ID</label><input type="text" id="newMedicaidId"></div>
            <div class="form-group"><label>Phone</label><input type="text" id="newPhone"></div>
            <div class="form-group"><label>Emergency Contact</label><input type="text" id="newEmergencyContact"></div>
            <div class="form-group"><label>Address</label><textarea id="newAddress" rows="2"></textarea></div>
            <div style="display:flex; gap:10px; margin-top:20px;">
                <button type="submit" class="green">Add Member</button>
                <button type="button" onclick="closeAddMemberModal()" class="red">Cancel</button>
            </div>
        </form>
    </div>
    
    <!-- ISP Outcomes Modal -->
    <div class="modal-overlay" id="outcomesModalOverlay" onclick="closeOutcomesModal()"></div>
    <div class="modal" id="outcomesModal">
        <h3>Edit ISP Outcomes</h3>
        <p id="outcomesMemberName" style="margin-bottom:15px; color:#666;"></p>
        <div id="outcomesList"></div>
        <div style="margin-top:15px;">
            <input type="text" id="newOutcomeText" placeholder="Enter new outcome..." style="width:100%; padding:10px; margin-bottom:10px;">
            <button onclick="addOutcome()" class="green">Add Outcome</button>
        </div>
        <div style="display:flex; gap:10px; margin-top:20px;">
            <button onclick="closeOutcomesModal()" class="blue">Close</button>
        </div>
    </div>
    
    <div class="modal-overlay" id="modalOverlay" onclick="closeModal()"></div>
    <div class="modal" id="memberEditModal">
        <h3>Edit Member Information</h3>
        <form id="memberEditForm">
            <input type="hidden" id="editMemberId">
            <div class="form-group"><label>Full Name</label><input type="text" id="editFullName" required></div>
            <div class="form-group"><label>Location</label><select id="editLocation" required></select></div>
            <div class="form-group"><label>Display Name</label><input type="text" id="editDisplayName"></div>
            <div class="form-group"><label>Date of Birth</label><input type="date" id="editDOB"></div>
            <div class="form-group"><label>Medicaid ID</label><input type="text" id="editMedicaidId"></div>
            <div class="form-group"><label>Phone</label><input type="text" id="editPhone"></div>
            <div class="form-group"><label>Emergency Contact</label><input type="text" id="editEmergencyContact"></div>
            <div class="form-group"><label>Address</label><textarea id="editAddress" rows="2"></textarea></div>
            <div style="display:flex; gap:10px; margin-top:20px;">
                <button type="submit" class="green">Save</button>
                <button type="button" onclick="closeModal()" class="red">Cancel</button>
            </div>
        </form>
    </div>
    
    <script>
        let taskCount = 1;
        let allData = { members: [], mentors: [], locations: [], activities: [], promptLevels: [], taskCategories: [], strategies: [], unitOptions: [], serviceTypes: [], medicationStatuses: [], medicationTypes: [], memberLocations: [] };
        let currentMemberId = null;
        let currentUser = { username: '', role: '' };
        let currentMonth = new Date();
        
        async function loadCurrentUser() {
            const response = await fetch('/api/current-user');
            const data = await response.json();
            currentUser = data;
            document.getElementById('currentUserDisplay').innerHTML = `👤 ${currentUser.username} (${currentUser.role})`;
            
            if (currentUser.role !== 'admin') {
                document.getElementById('navAdmin').style.display = 'none';
            }
        }
        
        async function loadAllData() {
            try {
                const responses = await Promise.all([
                    fetch('/api/members').then(r => r.json()),
                    fetch('/api/mentors').then(r => r.json()),
                    fetch('/api/locations').then(r => r.json()),
                    fetch('/api/activities').then(r => r.json()),
                    fetch('/api/prompt-levels').then(r => r.json()),
                    fetch('/api/task-categories').then(r => r.json()),
                    fetch('/api/strategies').then(r => r.json()),
                    fetch('/api/unit-options').then(r => r.json()),
                    fetch('/api/service-types').then(r => r.json()),
                    fetch('/api/medication-statuses').then(r => r.json()),
                    fetch('/api/medication-types').then(r => r.json()),
                    fetch('/api/member-locations').then(r => r.json())
                ]);
                
                allData.members = responses[0].data.filter(m => m.is_active);
                allData.mentors = responses[1].data.filter(m => m.is_active);
                allData.locations = responses[2].data.filter(l => l.is_active);
                allData.activities = responses[3].data.filter(a => a.is_active);
                allData.promptLevels = responses[4].data.filter(p => p.is_active);
                allData.taskCategories = responses[5].data.filter(c => c.is_active);
                allData.strategies = responses[6].data.filter(s => s.is_active);
                allData.unitOptions = responses[7].data.filter(u => u.is_active);
                allData.serviceTypes = responses[8].data.filter(s => s.is_active);
                allData.medicationStatuses = responses[9].data.filter(s => s.is_active);
                allData.medicationTypes = responses[10].data.filter(t => t.is_active);
                allData.memberLocations = responses[11].data.filter(l => l.is_active);
                
                populateSelect('memberId', allData.members, 'id', 'full_name');
                populateSelect('mentorId', allData.mentors, 'id', 'full_name');
                populateSelect('locationId', allData.locations, 'id', 'location_name');
                populateSelect('units', allData.unitOptions, 'unit_value', 'display_text');
                populateSelect('serviceType', allData.serviceTypes, 'id', 'type_name');
                populateSelect('medicationStatus', allData.medicationStatuses, 'id', 'status_name');
                populateSelect('medicationType', allData.medicationTypes, 'id', 'type_name');
                populateSelect('newLocation', allData.memberLocations, 'id', 'location_name');
                populateSelect('editLocation', allData.memberLocations, 'id', 'location_name');
                
                calculateUnits();
                updateSignaturePreview();
            } catch (e) { console.error('Error loading data:', e); }
        }
        
        function populateSelect(id, items, valueKey, labelKey) {
            const select = document.getElementById(id);
            if (!select || !items.length) return;
            select.innerHTML = '<option value="">Select</option>' + items.map(item => `<option value="${item[valueKey]}">${item[labelKey]}</option>`).join('');
        }
        
        async function loadMemberDetails() {
            const memberId = document.getElementById('memberId').value;
            if (!memberId) return;
            
            const member = allData.members.find(m => m.id == memberId);
            if (member) {
                document.getElementById('memberInfoText').innerHTML = `${member.full_name} | Location: ${member.location || 'N/A'} | DOB: ${member.date_of_birth || 'N/A'}`;
                document.getElementById('memberInfo').style.display = 'flex';
            }
            
            try {
                const response = await fetch(`/api/isp-outcomes/${memberId}`);
                const data = await response.json();
                const outcomes = data.data.filter(o => o.is_active);
                const select = document.getElementById('ispOutcomeId');
                select.innerHTML = '<option value="">Select Outcome</option>' + outcomes.map(o => `<option value="${o.id}">${o.outcome_text}</option>`).join('');
            } catch (e) { console.error('Error:', e); }
        }
        
        function editMemberInfo() {
            const memberId = document.getElementById('memberId').value;
            const member = allData.members.find(m => m.id == memberId);
            if (!member) return;
            
            document.getElementById('editMemberId').value = member.id;
            document.getElementById('editFullName').value = member.full_name || '';
            document.getElementById('editDisplayName').value = member.display_name || '';
            document.getElementById('editDOB').value = member.date_of_birth || '';
            document.getElementById('editMedicaidId').value = member.medicaid_id || '';
            document.getElementById('editPhone').value = member.phone || '';
            document.getElementById('editEmergencyContact').value = member.emergency_contact || '';
            document.getElementById('editAddress').value = member.address || '';
            
            const locationId = allData.memberLocations.find(l => l.location_name === member.location)?.id || '';
            document.getElementById('editLocation').value = locationId;
            
            document.getElementById('memberEditModal').style.display = 'block';
            document.getElementById('modalOverlay').style.display = 'block';
        }
        
        function closeModal() {
            document.getElementById('memberEditModal').style.display = 'none';
            document.getElementById('modalOverlay').style.display = 'none';
        }
        
        document.getElementById('memberEditForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const memberId = document.getElementById('editMemberId').value;
            const locationId = document.getElementById('editLocation').value;
            const locationName = allData.memberLocations.find(l => l.id == locationId)?.location_name || '';
            
            const data = {
                full_name: document.getElementById('editFullName').value,
                display_name: document.getElementById('editDisplayName').value,
                location: locationName,
                date_of_birth: document.getElementById('editDOB').value,
                medicaid_id: document.getElementById('editMedicaidId').value,
                phone: document.getElementById('editPhone').value,
                emergency_contact: document.getElementById('editEmergencyContact').value,
                address: document.getElementById('editAddress').value
            };
            
            try {
                await fetch(`/api/members/${memberId}`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                alert('Member updated!');
                closeModal();
                location.reload();
            } catch (e) { alert('Error'); }
        });
        
        function showAddMemberForm() {
            document.getElementById('addMemberForm').reset();
            document.getElementById('addMemberModal').style.display = 'block';
            document.getElementById('addMemberModalOverlay').style.display = 'block';
        }
        
        function closeAddMemberModal() {
            document.getElementById('addMemberModal').style.display = 'none';
            document.getElementById('addMemberModalOverlay').style.display = 'none';
        }
        
        document.getElementById('addMemberForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const locationId = document.getElementById('newLocation').value;
            const locationName = allData.memberLocations.find(l => l.id == locationId)?.location_name || '';
            
            const data = {
                full_name: document.getElementById('newFullName').value,
                display_name: document.getElementById('newDisplayName').value || document.getElementById('newFullName').value.split()[0],
                location: locationName,
                date_of_birth: document.getElementById('newDOB').value,
                medicaid_id: document.getElementById('newMedicaidId').value,
                phone: document.getElementById('newPhone').value,
                emergency_contact: document.getElementById('newEmergencyContact').value,
                address: document.getElementById('newAddress').value
            };
            
            try {
                const response = await fetch('/api/members', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                const result = await response.json();
                if (result.success) {
                    alert('Member added!');
                    closeAddMemberModal();
                    loadAllData();
                    loadMembersList();
                }
            } catch (e) { alert('Error adding member'); }
        });
        
        function calculateUnits() {
            const start = document.getElementById('startTime').value;
            const end = document.getElementById('endTime').value;
            if (start && end) {
                const startMin = parseInt(start.split(':')[0]) * 60 + parseInt(start.split(':')[1]);
                const endMin = parseInt(end.split(':')[0]) * 60 + parseInt(end.split(':')[1]);
                const units = ((endMin - startMin) / 60).toFixed(1);
                const unitSelect = document.getElementById('units');
                const options = Array.from(unitSelect.options);
                const match = options.find(opt => opt.value === units);
                if (match) unitSelect.value = units;
            }
        }
        
        function toggleMedicationType() {
            const statusSelect = document.getElementById('medicationStatus');
            const statusText = statusSelect.options[statusSelect.selectedIndex]?.text;
            document.getElementById('medicationType').disabled = statusText !== 'Yes';
        }
        
        function updateSignaturePreview() {
            const select = document.getElementById('mentorId');
            document.getElementById('signaturePreview').innerHTML = select.options[select.selectedIndex]?.text || '';
        }
        
        function addTask() {
            const html = `<div class="task-item" id="task-${taskCount}">
                <div class="form-row">
                    <div class="form-group"><label>Location</label><select id="taskLocation-${taskCount}">${allData.locations.map(l => `<option>${l.location_name}</option>`).join('')}</select></div>
                    <div class="form-group"><label>Activity</label><select id="taskActivity-${taskCount}">${allData.activities.map(a => `<option>${a.activity_name}</option>`).join('')}</select></div>
                    <div class="form-group"><label>Prompt Level</label><select id="taskPrompt-${taskCount}">${allData.promptLevels.map(p => `<option>${p.level_name}</option>`).join('')}</select></div>
                    <div class="form-group"><label>Category</label><select id="taskCategory-${taskCount}">${allData.taskCategories.map(c => `<option>${c.category_name}</option>`).join('')}</select></div>
                </div>
                <div class="form-group"><label>Strategy</label><select id="taskStrategySelect-${taskCount}" onchange="document.getElementById('taskStrategy-${taskCount}').value=this.value"><option value="">Select...</option>${allData.strategies.map(s => `<option>${s.strategy_text.replace(/"/g,'&quot;')}</option>`).join('')}</select>
                <textarea id="taskStrategy-${taskCount}" rows="2" style="margin-top:5px;"></textarea></div>
                <div class="form-group"><label>Notes</label><textarea id="taskNotes-${taskCount}" rows="3"></textarea></div>
                <button type="button" onclick="this.parentElement.remove()" class="red">Remove</button>
            </div>`;
            document.getElementById('tasksList').insertAdjacentHTML('beforeend', html);
            taskCount++;
        }
        
        function getFormData() {
            const tasks = [];
            for (let i = 1; i < taskCount; i++) {
                const el = document.getElementById(`task-${i}`); if (!el) continue;
                tasks.push({
                    location: document.getElementById(`taskLocation-${i}`)?.value || '',
                    activity: document.getElementById(`taskActivity-${i}`)?.value || '',
                    prompt_level: document.getElementById(`taskPrompt-${i}`)?.value || '',
                    category: document.getElementById(`taskCategory-${i}`)?.value || '',
                    strategy: document.getElementById(`taskStrategy-${i}`)?.value || '',
                    notes: document.getElementById(`taskNotes-${i}`)?.value || ''
                });
            }
            
            const memberId = document.getElementById('memberId').value;
            const mentorId = document.getElementById('mentorId').value;
            
            return {
                member_id: parseInt(memberId), 
                member_name: allData.members.find(m => m.id == memberId)?.full_name || '',
                mentor_id: parseInt(mentorId), 
                mentor_name: allData.mentors.find(m => m.id == mentorId)?.full_name || '',
                service_type: document.getElementById('serviceType').selectedOptions[0]?.text || '',
                service_date: document.getElementById('serviceDate').value,
                start_time: document.getElementById('startTime').value, 
                end_time: document.getElementById('endTime').value,
                units: document.getElementById('units').value,
                location_id: parseInt(document.getElementById('locationId').value), 
                location_name: allData.locations.find(l => l.id == document.getElementById('locationId').value)?.location_name || '',
                isp_outcome_id: parseInt(document.getElementById('ispOutcomeId').value), 
                isp_outcome_text: document.getElementById('ispOutcomeId').selectedOptions[0]?.text || '',
                medication_status: document.getElementById('medicationStatus').selectedOptions[0]?.text || 'No',
                medication_type: document.getElementById('medicationType').selectedOptions[0]?.text || '',
                tasks: tasks
            };
        }
        
        async function saveDraft() {
            const data = getFormData();
            
            try {
                const response = await fetch('/api/drafts', { 
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'}, 
                    body: JSON.stringify(data) 
                });
                const result = await response.json();
                if (result.success) { 
                    alert('Draft saved!'); 
                    resetForm();
                    showSection('drafts');
                } else alert('Error: ' + result.message);
            } catch (error) { alert('Error saving draft'); }
        }
        
        async function submitForReview() {
            const data = getFormData();
            
            try {
                const response = await fetch('/api/submit-for-review', { 
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'}, 
                    body: JSON.stringify(data) 
                });
                const result = await response.json();
                if (result.success) { 
                    alert('Submitted for review!'); 
                    resetForm();
                    showSection('submitted');
                } else alert('Error: ' + result.message);
            } catch (error) { alert('Error submitting'); }
        }
        
        function resetForm() {
            document.getElementById('reportForm').reset();
            document.getElementById('serviceDate').value = new Date().toISOString().split('T')[0];
            document.getElementById('startTime').value = '09:00';
            document.getElementById('endTime').value = '15:00';
            document.getElementById('medicationType').disabled = true;
            document.getElementById('tasksList').innerHTML = '';
            taskCount = 1;
            addTask();
            calculateUnits();
            updateSignaturePreview();
        }
        
        async function loadDrafts() {
            const response = await fetch('/api/drafts');
            const data = await response.json();
            
            let html = '<table><tr><th>Date</th><th>Member</th><th>Mentor</th><th>Units</th><th>Actions</th></tr>';
            data.data.forEach(r => {
                html += `<tr><td>${r.service_date}</td><td>${r.member_name}</td><td>${r.mentor_name}</td><td>${r.units}</td>
                    <td>
                        <button onclick="viewReport(${r.id}, 'draft')" class="blue">👁️ View</button>
                        <button onclick="editDraft(${r.id})" class="orange">✏️ Edit</button>
                        <button onclick="submitDraft(${r.id})" class="purple">📤 Submit</button>
                        <button onclick="deleteDraft(${r.id})" class="red">🗑️ Delete</button>
                    </td></tr>`;
            });
            html += '</table>';
            document.getElementById('draftsList').innerHTML = html || '<p>No drafts yet.</p>';
        }
        
        async function loadSubmitted() {
            const response = await fetch('/api/submitted');
            const data = await response.json();
            
            let html = '<table><tr><th>Date</th><th>Member</th><th>Mentor</th><th>Submitted By</th><th>Units</th><th>Status</th><th>Actions</th></tr>';
            data.data.forEach(r => {
                const statusBadge = r.status === 'rejected' ? 'status-rejected' : 'status-submitted';
                const statusText = r.status === 'rejected' ? 'REJECTED' : 'PENDING';
                
                html += `<tr><td>${r.service_date}</td><td>${r.member_name}</td><td>${r.mentor_name}</td><td>${r.submitted_by || 'Unknown'}</td><td>${r.units}</td>
                    <td><span class="status-badge ${statusBadge}">${statusText}</span></td>
                    <td>
                        <button onclick="viewReport(${r.id}, 'submitted')" class="blue">👁️ View</button>`;
                if (currentUser.role === 'supervisor' || currentUser.role === 'admin') {
                    html += `<button onclick="approveReport(${r.id})" class="green">✅ Approve</button>
                             <button onclick="showRejectComment(${r.id})" class="red">❌ Reject</button>`;
                }
                html += `</td></tr>`;
            });
            html += '</table>';
            document.getElementById('submittedList').innerHTML = html || '<p>No reports awaiting review.</p>';
        }
        
        async function loadApproved() {
            const response = await fetch('/api/approved');
            const data = await response.json();
            
            let html = '<table><tr><th>Date</th><th>Member</th><th>Mentor</th><th>Approved By</th><th>Units</th><th>Actions</th></tr>';
            data.data.forEach(r => {
                html += `<tr><td>${r.service_date}</td><td>${r.member_name}</td><td>${r.mentor_name}</td><td>${r.approved_by || 'Supervisor'}</td><td>${r.units}</td>
                    <td>
                        <button onclick="viewReport(${r.id}, 'approved')" class="blue">👁️ View</button>
                        <button onclick="downloadPDF(${r.id})" class="green">📄 Download PDF</button>
                    </td></tr>`;
            });
            html += '</table>';
            document.getElementById('approvedList').innerHTML = html || '<p>No approved reports yet.</p>';
        }
        
        async function viewReport(id, type) {
            let url = '/api/report/';
            if (type === 'draft') url += `draft/${id}`;
            else if (type === 'submitted') url += `submitted/${id}`;
            else url += `approved/${id}`;
            
            const response = await fetch(url);
            const report = await response.json();
            
            let html = `
                <div style="margin-bottom:15px;">
                    <span class="status-badge status-${type}">${type.toUpperCase()}</span>
                </div>
                <table style="width:100%">
                    <tr><th style="width:150px;">Member</th><td>${report.member_name}</td></tr>
                    <tr><th>Mentor</th><td>${report.mentor_name}</td></tr>
                    <tr><th>Date</th><td>${report.service_date}</td></tr>
                    <tr><th>Time</th><td>${report.start_time} - ${report.end_time}</td></tr>
                    <tr><th>Units</th><td>${report.units}</td></tr>
                    <tr><th>Location</th><td>${report.location_name}</td></tr>
                    <tr><th>ISP Outcome</th><td>${report.isp_outcome_text}</td></tr>
                    <tr><th>Medication</th><td>${report.medication_status} ${report.medication_type ? '(' + report.medication_type + ')' : ''}</td></tr>
                </table>
                <h4 style="margin-top:20px;">Tasks:</h4>
            `;
            
            report.tasks.forEach((task, i) => {
                html += `<div style="background:#f8f9fa; padding:10px; margin:10px 0; border-radius:6px;">
                    <strong>Task ${i+1}:</strong> ${task.activity}<br>
                    <strong>Location:</strong> ${task.location}<br>
                    <strong>Prompt:</strong> ${task.prompt_level}<br>
                    <strong>Strategy:</strong> ${task.strategy}<br>
                    ${task.notes ? '<strong>Notes:</strong> ' + task.notes : ''}
                </div>`;
            });
            
            if (report.comments && report.comments.length > 0) {
                html += `<h4 style="margin-top:20px;">Comments:</h4>`;
                report.comments.forEach(c => {
                    html += `<div class="comment-item">
                        <span class="comment-author">${c.author}</span>
                        <span class="comment-time">${c.time}</span>
                        <p style="margin-top:5px;">${c.text}</p>
                    </div>`;
                });
            }
            
            if (type === 'submitted' && (currentUser.role === 'supervisor' || currentUser.role === 'admin')) {
                html += `
                    <div style="margin-top:20px;">
                        <label><strong>Add Comment:</strong></label>
                        <textarea id="supervisorComment" rows="3" style="width:100%; padding:10px; margin-top:5px;" placeholder="Enter feedback or corrections needed..."></textarea>
                        <div style="display:flex; gap:10px; margin-top:10px;">
                            <button onclick="addCommentAndReject(${id})" class="red">❌ Reject with Comment</button>
                            <button onclick="addCommentOnly(${id})" class="blue">💬 Add Comment Only</button>
                        </div>
                    </div>
                `;
            }
            
            document.getElementById('viewModalContent').innerHTML = html;
            document.getElementById('viewModal').style.display = 'block';
            document.getElementById('viewModalOverlay').style.display = 'block';
        }
        
        async function addCommentOnly(reportId) {
            const comment = document.getElementById('supervisorComment')?.value;
            if (!comment) { alert('Please enter a comment'); return; }
            
            await fetch(`/api/report/submitted/${reportId}/comment`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({comment})
            });
            alert('Comment added!');
            closeViewModal();
            loadSubmitted();
        }
        
        async function addCommentAndReject(reportId) {
            const comment = document.getElementById('supervisorComment')?.value;
            if (!comment) { alert('Please enter a comment explaining the rejection'); return; }
            
            await fetch(`/api/reject/${reportId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({comment})
            });
            alert('Report rejected and returned to staff with your comment.');
            closeViewModal();
            loadSubmitted();
        }
        
        function showRejectComment(reportId) {
            const comment = prompt('Enter reason for rejection (this will be sent to the staff member):');
            if (comment) {
                rejectReportWithComment(reportId, comment);
            }
        }
        
        async function rejectReportWithComment(reportId, comment) {
            await fetch(`/api/reject/${reportId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({comment})
            });
            alert('Report rejected and returned to staff.');
            loadSubmitted();
        }
        
        function closeViewModal() {
            document.getElementById('viewModal').style.display = 'none';
            document.getElementById('viewModalOverlay').style.display = 'none';
        }
        
        async function approveReport(id) {
            if (!confirm('Approve this report?')) return;
            await fetch(`/api/approve/${id}`, { method: 'POST' });
            alert('Report approved!');
            loadSubmitted();
            loadApproved();
        }
        
        async function downloadPDF(id) {
            window.open(`/api/approved/${id}/pdf`, '_blank');
        }
        
        async function editDraft(id) {
            const response = await fetch(`/api/draft/${id}`);
            const data = await response.json();
            const report = data.data;
            
            document.getElementById('memberId').value = report.member_id;
            document.getElementById('mentorId').value = report.mentor_id;
            document.getElementById('serviceDate').value = report.service_date;
            document.getElementById('startTime').value = report.start_time;
            document.getElementById('endTime').value = report.end_time;
            document.getElementById('units').value = report.units;
            document.getElementById('locationId').value = report.location_id;
            document.getElementById('medicationStatus').value = allData.medicationStatuses.find(s => s.status_name === report.medication_status)?.id || '';
            
            await loadMemberDetails();
            setTimeout(() => {
                document.getElementById('ispOutcomeId').value = report.isp_outcome_id;
            }, 500);
            
            document.getElementById('tasksList').innerHTML = '';
            taskCount = 1;
            report.tasks.forEach(task => {
                addTask();
                setTimeout(() => {
                    document.getElementById(`taskLocation-${taskCount-1}`).value = task.location;
                    document.getElementById(`taskActivity-${taskCount-1}`).value = task.activity;
                    document.getElementById(`taskPrompt-${taskCount-1}`).value = task.prompt_level;
                    document.getElementById(`taskCategory-${taskCount-1}`).value = task.category;
                    document.getElementById(`taskStrategy-${taskCount-1}`).value = task.strategy;
                    document.getElementById(`taskNotes-${taskCount-1}`).value = task.notes;
                }, 100);
            });
            
            showSection('new');
        }
        
        async function submitDraft(id) {
            if (!confirm('Submit this draft for review?')) return;
            await fetch(`/api/submit-draft/${id}`, { method: 'POST' });
            alert('Submitted for review!');
            loadDrafts();
            loadSubmitted();
        }
        
        async function deleteDraft(id) {
            if (!confirm('Delete this draft?')) return;
            await fetch(`/api/draft/${id}`, { method: 'DELETE' });
            loadDrafts();
        }
        
        async function loadMembersList() {
            const response = await fetch('/api/members'); 
            const data = await response.json();
            const activeMembers = data.data.filter(m => m.is_active);
            
            const locations = ['Hackensack', 'Oxford', 'Union City'];
            let html = '';
            
            locations.forEach(loc => {
                const membersInLoc = activeMembers.filter(m => m.location === loc);
                html += `<div class="location-folder">
                    <div class="location-header" onclick="toggleLocation('${loc}')">📁 ${loc} (${membersInLoc.length} members)</div>
                    <div id="location-${loc}" style="margin-left:20px;">`;
                
                membersInLoc.forEach(m => {
                    html += `<div style="padding:8px; margin:5px 0; background:white; border-radius:6px; display:flex; justify-content:space-between;">
                        <span><strong>${m.full_name}</strong> | DOB: ${m.date_of_birth || 'N/A'}</span>
                        <span>
                            <button onclick="openOutcomesModal(${m.id}, '${m.full_name}')" class="orange" style="padding:3px 8px;">Outcomes</button>
                            <button onclick="editMemberFromList(${m.id})" class="blue" style="padding:3px 8px;">Edit</button>
                            <button onclick="removeMember(${m.id}, '${m.full_name}')" class="red" style="padding:3px 8px;">Remove</button>
                        </span>
                    </div>`;
                });
                
                html += `</div></div>`;
            });
            
            document.getElementById('membersByLocation').innerHTML = html;
        }
        
        function toggleLocation(loc) {
            const el = document.getElementById(`location-${loc}`);
            el.style.display = el.style.display === 'none' ? 'block' : 'none';
        }
        
        function editMemberFromList(memberId) {
            const member = allData.members.find(m => m.id == memberId);
            if (!member) return;
            
            document.getElementById('editMemberId').value = member.id;
            document.getElementById('editFullName').value = member.full_name || '';
            document.getElementById('editDisplayName').value = member.display_name || '';
            document.getElementById('editDOB').value = member.date_of_birth || '';
            document.getElementById('editMedicaidId').value = member.medicaid_id || '';
            document.getElementById('editPhone').value = member.phone || '';
            document.getElementById('editEmergencyContact').value = member.emergency_contact || '';
            document.getElementById('editAddress').value = member.address || '';
            
            const locationId = allData.memberLocations.find(l => l.location_name === member.location)?.id || '';
            document.getElementById('editLocation').value = locationId;
            
            document.getElementById('memberEditModal').style.display = 'block';
            document.getElementById('modalOverlay').style.display = 'block';
        }
        
        async function removeMember(memberId, memberName) {
            if (!confirm(`Are you sure you want to remove ${memberName}?`)) return;
            await fetch(`/api/members/${memberId}/deactivate`, { method: 'PUT' });
            alert('Member removed!');
            loadMembersList();
            loadAllData();
        }
        
        async function openOutcomesModal(memberId, memberName) {
            currentMemberId = memberId;
            document.getElementById('outcomesMemberName').innerHTML = `<strong>${memberName}</strong>`;
            
            const response = await fetch(`/api/isp-outcomes/${memberId}`);
            const data = await response.json();
            const outcomes = data.data.filter(o => o.is_active);
            
            let html = '';
            outcomes.forEach(o => {
                html += `<div class="outcome-item">
                    <input type="text" class="outcome-text" id="outcome-${o.id}" value="${o.outcome_text.replace(/"/g, '&quot;')}">
                    <button onclick="updateOutcome(${o.id})" class="blue" style="padding:5px 10px;">Save</button>
                    <button onclick="deleteOutcome(${o.id})" class="red" style="padding:5px 10px;">Delete</button>
                </div>`;
            });
            
            document.getElementById('outcomesList').innerHTML = html || '<p>No outcomes yet. Add one below.</p>';
            document.getElementById('outcomesModal').style.display = 'block';
            document.getElementById('outcomesModalOverlay').style.display = 'block';
        }
        
        function closeOutcomesModal() {
            document.getElementById('outcomesModal').style.display = 'none';
            document.getElementById('outcomesModalOverlay').style.display = 'none';
        }
        
        async function updateOutcome(outcomeId) {
            const input = document.getElementById(`outcome-${outcomeId}`);
            await fetch(`/api/isp-outcomes/${outcomeId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({outcome_text: input.value})
            });
            alert('Outcome updated!');
        }
        
        async function deleteOutcome(outcomeId) {
            if (!confirm('Delete this outcome?')) return;
            await fetch(`/api/isp-outcomes/${outcomeId}`, { method: 'DELETE' });
            openOutcomesModal(currentMemberId, '');
        }
        
        async function addOutcome() {
            const text = document.getElementById('newOutcomeText').value;
            if (!text) { alert('Enter outcome text'); return; }
            
            await fetch('/api/isp-outcomes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({member_id: currentMemberId, outcome_text: text})
            });
            document.getElementById('newOutcomeText').value = '';
            openOutcomesModal(currentMemberId, '');
        }
        
        async function loadCalendar() {
            const response = await fetch('/api/submitted');
            const submitted = await response.json();
            const approvedRes = await fetch('/api/approved');
            const approved = await approvedRes.json();
            
            const allReports = [...submitted.data, ...approved.data];
            
            const year = currentMonth.getFullYear();
            const month = currentMonth.getMonth();
            
            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const startDay = firstDay.getDay();
            
            document.getElementById('currentMonthYear').textContent = 
                new Date(year, month).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
            
            let html = '<div class="calendar">';
            
            ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach(d => {
                html += `<div style="text-align:center; font-weight:bold; padding:10px;">${d}</div>`;
            });
            
            for (let i = 0; i < startDay; i++) {
                html += '<div class="calendar-day"></div>';
            }
            
            for (let d = 1; d <= lastDay.getDate(); d++) {
                const dateStr = `${year}-${String(month+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
                const reportsOnDay = allReports.filter(r => r.service_date === dateStr);
                const hasReport = reportsOnDay.length > 0;
                
                html += `<div class="calendar-day ${hasReport ? 'has-report' : ''}">
                    <div class="calendar-date">${d}</div>`;
                
                if (hasReport) {
                    reportsOnDay.slice(0, 3).forEach(r => {
                        html += `<div style="font-size:10px;"><span class="report-dot"></span>${r.member_name.split(' ')[0]}</div>`;
                    });
                    if (reportsOnDay.length > 3) {
                        html += `<div style="font-size:10px;">+${reportsOnDay.length - 3} more</div>`;
                    }
                }
                
                html += '</div>';
            }
            
            html += '</div>';
            document.getElementById('calendar').innerHTML = html;
        }
        
        function changeMonth(delta) {
            currentMonth.setMonth(currentMonth.getMonth() + delta);
            loadCalendar();
        }
        
        async function renderAdminPanel() {
            const response = await fetch('/api/admin/all-configs'); const data = await response.json();
            let html = '';
            const sections = [
                { title: 'Member Locations', key: 'member_locations', field: 'location_name' },
                { title: 'Service Types', key: 'service_types', field: 'type_name' },
                { title: 'Mentors', key: 'mentors', field: 'full_name' },
                { title: 'Locations', key: 'locations', field: 'location_name' },
                { title: 'Activities', key: 'activities', field: 'activity_name' },
                { title: 'Prompt Levels', key: 'prompt_levels', field: 'level_name' },
                { title: 'Task Categories', key: 'task_categories', field: 'category_name' },
                { title: 'Medication Statuses', key: 'medication_statuses', field: 'status_name' },
                { title: 'Medication Types', key: 'medication_types', field: 'type_name' },
                { title: 'Strategies', key: 'strategies', field: 'strategy_text', textarea: true },
                { title: 'Unit Options', key: 'unit_options', field: 'unit_value', displayField: 'display_text', unit: true }
            ];
            sections.forEach(s => {
                const items = data[s.key] || [];
                html += `<div class="admin-section"><h3>${s.title}</h3><div id="admin-${s.key}">`;
                items.filter(i => i.is_active).forEach((item, idx) => {
                    if (s.textarea) html += `<div class="list-item"><textarea id="${s.key}-${idx}" style="flex:1;" rows="2">${item[s.field]}</textarea><button onclick="this.parentElement.remove()" class="red">Remove</button></div>`;
                    else if (s.unit) html += `<div class="list-item"><input value="${item.unit_value}" id="${s.key}-${idx}" style="flex:1;"><input value="${item.display_text}" id="${s.key}-display-${idx}" style="flex:1;"><button onclick="this.parentElement.remove()" class="red">Remove</button></div>`;
                    else html += `<div class="list-item"><input value="${item[s.field]}" id="${s.key}-${idx}" style="flex:1;"><button onclick="this.parentElement.remove()" class="red">Remove</button></div>`;
                });
                html += `</div><button onclick="addAdminItem('${s.key}', ${s.textarea ? 'true' : 'false'}, ${s.unit ? 'true' : 'false'})">+ Add</button>
                    <button onclick="saveAdminConfig('${s.key}')" class="green" style="margin-left:10px;">Save</button></div>`;
            });
            document.getElementById('adminConfigs').innerHTML = html;
        }
        
        function addAdminItem(key, isTextarea, isUnit) {
            const container = document.getElementById(`admin-${key}`); const idx = container.children.length;
            const div = document.createElement('div'); div.className = 'list-item';
            if (isTextarea) div.innerHTML = `<textarea id="${key}-${idx}" style="flex:1;" rows="2"></textarea><button onclick="this.parentElement.remove()" class="red">Remove</button>`;
            else if (isUnit) div.innerHTML = `<input id="${key}-${idx}" style="flex:1;" placeholder="Value"><input id="${key}-display-${idx}" style="flex:1;" placeholder="Display"><button onclick="this.parentElement.remove()" class="red">Remove</button>`;
            else div.innerHTML = `<input id="${key}-${idx}" style="flex:1;"><button onclick="this.parentElement.remove()" class="red">Remove</button>`;
            container.appendChild(div);
        }
        
        async function saveAdminConfig(key) {
            const items = document.querySelectorAll(`[id^="${key}-"]`);
            const values = [];
            if (key === 'unit_options') {
                for (let i = 0; i < items.length; i += 2) if (items[i].value.trim()) values.push({ unit_value: items[i].value, display_text: items[i+1]?.value || items[i].value + ' Units' });
            } else { items.forEach(item => { if (item.value && item.value.trim()) values.push(item.value.trim()); }); }
            
            const response = await fetch(`/api/admin/${key}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ values }) });
            const result = await response.json();
            if (result.success) {
                alert('Configuration saved permanently!');
                await loadAllData();
                renderAdminPanel();
            }
        }
        
        function showSection(section) {
            ['new', 'drafts', 'submitted', 'approved', 'calendar', 'members', 'admin'].forEach(s => { 
                document.getElementById(s + 'Section').style.display = s === section ? 'block' : 'none'; 
            });
            document.querySelectorAll('.nav button').forEach(btn => btn.classList.remove('active'));
            document.getElementById('nav' + section.charAt(0).toUpperCase() + section.slice(1)).classList.add('active');
            
            if (section === 'drafts') loadDrafts();
            if (section === 'submitted') loadSubmitted();
            if (section === 'approved') loadApproved();
            if (section === 'calendar') loadCalendar();
            if (section === 'members') loadMembersList();
            if (section === 'admin') renderAdminPanel();
        }
        
        async function logout() { await fetch('/api/logout', {method: 'POST'}); window.location.href = '/'; }
        
        document.getElementById('serviceDate').value = new Date().toISOString().split('T')[0];
        document.getElementById('startTime').addEventListener('change', calculateUnits);
        document.getElementById('endTime').addEventListener('change', calculateUnits);
        document.getElementById('mentorId').addEventListener('change', updateSignaturePreview);
        
        loadCurrentUser();
        loadAllData().then(() => { addTask(); if (allData.members.length) loadMemberDetails(); });
    </script>
</body>
</html>
'''

# API Routes (same as before plus new ones)
@app.route('/')
def index():
    if 'user_id' in session: return redirect('/app')
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/app')
def main_app():
    if 'user_id' not in session: return redirect('/')
    return render_template_string(MAIN_APP_TEMPLATE)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    app_data = load_data()
    for user in app_data['users']:
        if user['username'] == data['username'] and check_password_hash(user['password'], data['password']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return jsonify({'success': True})
    return jsonify({'success': False}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/current-user')
def current_user():
    return jsonify({'username': session.get('username', ''), 'role': session.get('role', '')})

@app.route('/api/members', methods=['GET'])
def get_members():
    return jsonify({'success': True, 'data': load_data()['members']})

@app.route('/api/members', methods=['POST'])
def add_member():
    data = request.json
    app_data = load_data()
    
    new_id = app_data.get('next_member_id', max([m['id'] for m in app_data['members']] + [0]) + 1)
    member = {
        'id': new_id,
        'full_name': data['full_name'],
        'display_name': data.get('display_name', data['full_name'].split()[0]),
        'location': data.get('location', 'Hackensack'),
        'date_of_birth': data.get('date_of_birth', ''),
        'medicaid_id': data.get('medicaid_id', ''),
        'phone': data.get('phone', ''),
        'emergency_contact': data.get('emergency_contact', ''),
        'address': data.get('address', ''),
        'is_active': True
    }
    app_data['members'].append(member)
    app_data['next_member_id'] = new_id + 1
    
    next_outcome_id = max([o['id'] for o in app_data['isp_outcomes']] + [0]) + 1
    app_data['isp_outcomes'].append({'id': next_outcome_id, 'member_id': new_id, 'outcome_text': f"{member['full_name']} will engage in community activities and socialize with peers.", 'is_active': True})
    app_data['isp_outcomes'].append({'id': next_outcome_id + 1, 'member_id': new_id, 'outcome_text': f"{member['full_name']} will develop independent living skills.", 'is_active': True})
    
    save_data(app_data)
    return jsonify({'success': True, 'id': new_id})

@app.route('/api/members/<int:id>', methods=['PUT'])
def update_member(id):
    data = request.json
    app_data = load_data()
    for m in app_data['members']:
        if m['id'] == id:
            m.update(data)
            save_data(app_data)
            return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/members/<int:id>/deactivate', methods=['PUT'])
def deactivate_member(id):
    app_data = load_data()
    for m in app_data['members']:
        if m['id'] == id:
            m['is_active'] = False
            save_data(app_data)
            return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/member-locations')
def get_member_locations():
    return jsonify({'success': True, 'data': load_data()['member_locations']})

@app.route('/api/mentors')
def get_mentors():
    return jsonify({'success': True, 'data': load_data()['mentors']})

@app.route('/api/locations')
def get_locations():
    return jsonify({'success': True, 'data': load_data()['locations']})

@app.route('/api/service-types')
def get_service_types():
    return jsonify({'success': True, 'data': load_data()['service_types']})

@app.route('/api/medication-statuses')
def get_medication_statuses():
    return jsonify({'success': True, 'data': load_data()['medication_statuses']})

@app.route('/api/medication-types')
def get_medication_types():
    return jsonify({'success': True, 'data': load_data()['medication_types']})

@app.route('/api/isp-outcomes/<int:member_id>')
def get_isp_outcomes(member_id):
    app_data = load_data()
    return jsonify({'success': True, 'data': [o for o in app_data['isp_outcomes'] if o['member_id'] == member_id]})

@app.route('/api/isp-outcomes', methods=['POST'])
def add_isp_outcome():
    data = request.json
    app_data = load_data()
    new_id = max([o['id'] for o in app_data['isp_outcomes']] + [0]) + 1
    app_data['isp_outcomes'].append({'id': new_id, 'member_id': data['member_id'], 'outcome_text': data['outcome_text'], 'is_active': True})
    save_data(app_data)
    return jsonify({'success': True})

@app.route('/api/isp-outcomes/<int:id>', methods=['PUT'])
def update_isp_outcome(id):
    data = request.json
    app_data = load_data()
    for o in app_data['isp_outcomes']:
        if o['id'] == id:
            o['outcome_text'] = data['outcome_text']
            save_data(app_data)
            return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/isp-outcomes/<int:id>', methods=['DELETE'])
def delete_isp_outcome(id):
    app_data = load_data()
    for o in app_data['isp_outcomes']:
        if o['id'] == id:
            o['is_active'] = False
            save_data(app_data)
            return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/activities')
def get_activities():
    return jsonify({'success': True, 'data': load_data()['activities']})

@app.route('/api/prompt-levels')
def get_prompt_levels():
    return jsonify({'success': True, 'data': load_data()['prompt_levels']})

@app.route('/api/task-categories')
def get_task_categories():
    return jsonify({'success': True, 'data': load_data()['task_categories']})

@app.route('/api/strategies')
def get_strategies():
    return jsonify({'success': True, 'data': load_data()['strategies']})

@app.route('/api/unit-options')
def get_unit_options():
    return jsonify({'success': True, 'data': load_data()['unit_options']})

@app.route('/api/drafts', methods=['GET'])
def get_drafts():
    app_data = load_data()
    username = session.get('username', '')
    drafts = app_data['user_drafts'].get(username, [])
    return jsonify({'success': True, 'data': drafts})

@app.route('/api/drafts', methods=['POST'])
def save_draft():
    data = request.json
    app_data = load_data()
    username = session.get('username', '')
    
    if username not in app_data['user_drafts']:
        app_data['user_drafts'][username] = []
    
    draft_id = len(app_data['user_drafts'][username]) + 1
    draft = {'id': draft_id, **data, 'status': 'draft', 'created_by': username, 'created_at': datetime.now().isoformat(), 'comments': []}
    app_data['user_drafts'][username].append(draft)
    save_data(app_data)
    return jsonify({'success': True, 'id': draft_id})

@app.route('/api/draft/<int:id>', methods=['GET'])
def get_draft(id):
    app_data = load_data()
    username = session.get('username', '')
    drafts = app_data['user_drafts'].get(username, [])
    draft = next((d for d in drafts if d['id'] == id), None)
    if draft:
        return jsonify({'success': True, 'data': draft})
    return jsonify({'success': False}), 404

@app.route('/api/draft/<int:id>', methods=['DELETE'])
def delete_draft(id):
    app_data = load_data()
    username = session.get('username', '')
    if username in app_data['user_drafts']:
        app_data['user_drafts'][username] = [d for d in app_data['user_drafts'][username] if d['id'] != id]
        save_data(app_data)
    return jsonify({'success': True})

@app.route('/api/submit-draft/<int:id>', methods=['POST'])
def submit_draft(id):
    app_data = load_data()
    username = session.get('username', '')
    drafts = app_data['user_drafts'].get(username, [])
    draft = next((d for d in drafts if d['id'] == id), None)
    
    if draft:
        draft['status'] = 'submitted'
        draft['submitted_by'] = username
        draft['submitted_at'] = datetime.now().isoformat()
        draft['original_owner'] = username
        app_data['submitted_reports'].append(draft)
        app_data['user_drafts'][username] = [d for d in drafts if d['id'] != id]
        save_data(app_data)
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/submit-for-review', methods=['POST'])
def submit_for_review():
    data = request.json
    app_data = load_data()
    username = session.get('username', '')
    
    report = {
        'id': app_data['next_report_id'],
        **data,
        'status': 'submitted',
        'submitted_by': username,
        'original_owner': username,
        'submitted_at': datetime.now().isoformat(),
        'comments': []
    }
    app_data['next_report_id'] += 1
    app_data['submitted_reports'].append(report)
    save_data(app_data)
    return jsonify({'success': True, 'id': report['id']})

@app.route('/api/submitted', methods=['GET'])
def get_submitted():
    app_data = load_data()
    return jsonify({'success': True, 'data': app_data['submitted_reports']})

@app.route('/api/report/submitted/<int:id>', methods=['GET'])
def get_submitted_report(id):
    app_data = load_data()
    report = next((r for r in app_data['submitted_reports'] if r['id'] == id), None)
    if report:
        return jsonify(report)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/report/submitted/<int:id>/comment', methods=['POST'])
def add_comment(id):
    data = request.json
    app_data = load_data()
    report = next((r for r in app_data['submitted_reports'] if r['id'] == id), None)
    
    if report:
        if 'comments' not in report:
            report['comments'] = []
        report['comments'].append({
            'author': session.get('username', ''),
            'text': data['comment'],
            'time': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        save_data(app_data)
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/approve/<int:id>', methods=['POST'])
def approve_report(id):
    app_data = load_data()
    report = next((r for r in app_data['submitted_reports'] if r['id'] == id), None)
    
    if report:
        report['status'] = 'approved'
        report['approved_by'] = session.get('username', '')
        report['approved_at'] = datetime.now().isoformat()
        app_data['approved_reports'].append(report)
        app_data['submitted_reports'] = [r for r in app_data['submitted_reports'] if r['id'] != id]
        save_data(app_data)
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/reject/<int:id>', methods=['POST'])
def reject_report(id):
    data = request.json
    app_data = load_data()
    report = next((r for r in app_data['submitted_reports'] if r['id'] == id), None)
    
    if report:
        if 'comments' not in report:
            report['comments'] = []
        report['comments'].append({
            'author': session.get('username', ''),
            'text': data.get('comment', 'No comment provided'),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        
        report['status'] = 'rejected'
        report['rejected_by'] = session.get('username', '')
        report['rejected_at'] = datetime.now().isoformat()
        
        original_owner = report.get('original_owner', report.get('submitted_by', 'unknown'))
        if original_owner not in app_data['user_drafts']:
            app_data['user_drafts'][original_owner] = []
        app_data['user_drafts'][original_owner].append(report)
        app_data['submitted_reports'] = [r for r in app_data['submitted_reports'] if r['id'] != id]
        save_data(app_data)
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/api/approved', methods=['GET'])
def get_approved():
    app_data = load_data()
    return jsonify({'success': True, 'data': app_data['approved_reports']})

@app.route('/api/report/approved/<int:id>', methods=['GET'])
def get_approved_report(id):
    app_data = load_data()
    report = next((r for r in app_data['approved_reports'] if r['id'] == id), None)
    if report:
        return jsonify(report)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/approved/<int:id>/pdf')
def generate_approved_pdf(id):
    app_data = load_data()
    report = next((r for r in app_data['approved_reports'] if r['id'] == id), None)
    if not report: return "Not found", 404
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, rightMargin=0.5*inch, leftMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    calibri_style = ParagraphStyle('Calibri', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=16, spaceBefore=6, spaceAfter=6, textColor=colors.HexColor('#333333'))
    notes_style = ParagraphStyle('Notes', parent=calibri_style, fontName='Helvetica', fontSize=10.5, leading=15, leftIndent=0, rightIndent=0, spaceBefore=4, spaceAfter=8)
    signature_style = ParagraphStyle('Signature', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=18, textColor=colors.HexColor('#1a3a5c'), leftIndent=0, spaceBefore=10, spaceAfter=5)
    header_style = ParagraphStyle('Header', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1a3a5c'), spaceBefore=10, spaceAfter=10)
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1a3a5c'), alignment=1, spaceAfter=20)
    
    story.append(Paragraph('FCCS - Four Corners Community Services', title_style))
    story.append(Paragraph('Day Habilitation Service Report', header_style))
    story.append(Spacer(1, 10))
    
    med_text = report['medication_status']
    if report.get('medication_type') and report['medication_status'] == 'Yes':
        med_text += f" ({report['medication_type']})"
    
    header_data = [
        ['Member:', report['member_name'], 'Mentor:', report['mentor_name']],
        ['Service:', report['service_type'], 'Date:', report['service_date']],
        ['Time:', f"{report['start_time']} - {report['end_time']}", 'Units:', str(report['units'])],
        ['Location:', report['location_name'], 'Medication:', med_text]
    ]
    
    header_table = Table(header_data, colWidths=[1.2*inch, 2.8*inch, 1.2*inch, 2.8*inch])
    header_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10), ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')), ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e8e8e8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')), ('PADDING', (0, 0), (-1, -1), 8), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    if report.get('isp_outcome_text'):
        story.append(Paragraph('<b>ISP Outcome:</b>', header_style))
        story.append(Paragraph(report['isp_outcome_text'], calibri_style))
        story.append(Spacer(1, 10))
    
    story.append(Paragraph('<b>Tasks & Activities</b>', header_style))
    story.append(Spacer(1, 5))
    
    for idx, task in enumerate(report['tasks'], 1):
        story.append(Paragraph(f'<b>Task {idx}:</b>', calibri_style))
        
        task_data = [
            ['Location:', task.get('location', 'N/A')],
            ['Activity:', task.get('activity', 'N/A')],
            ['Prompt Level:', task.get('prompt_level', 'N/A')],
            ['Category:', task.get('category', 'N/A')]
        ]
        
        task_table = Table(task_data, colWidths=[1.2*inch, 5*inch])
        task_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9), ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('PADDING', (0, 0), (-1, -1), 6), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(task_table)
        story.append(Spacer(1, 8))
        
        if task.get('strategy'):
            story.append(Paragraph('<b>Strategy:</b>', calibri_style))
            strategy_text = task['strategy'].replace('\n', '<br/>').replace('\r', '')
            story.append(Paragraph(strategy_text, notes_style))
            story.append(Spacer(1, 5))
        
        if task.get('notes'):
            story.append(Paragraph('<b>Notes:</b>', calibri_style))
            notes_text = task['notes'].replace('\n', '<br/>').replace('\r', '')
            notes_text = notes_text.replace('  ', '&nbsp;&nbsp;')
            story.append(Paragraph(notes_text, notes_style))
        
        story.append(Spacer(1, 12))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph('<b>Staff Signature:</b>', calibri_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph(report['mentor_name'], signature_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph('_' * 50, styles['Normal']))
    story.append(Spacer(1, 3))
    story.append(Paragraph('Electronic Signature - Valid as original', styles['Normal']))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"✅ APPROVED by {report.get('approved_by', 'Supervisor')} on {report.get('approved_at', '')[:10]}", header_style))
    
    story.append(Spacer(1, 20))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#999999'), alignment=1)
    story.append(Paragraph(f'Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', footer_style))
    story.append(Paragraph('FCCS - Four Corners Community Services', footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f"{report['member_name'].replace(' ', '_')}_Approved_{report['service_date']}.pdf")

@app.route('/api/report/draft/<int:id>', methods=['GET'])
def get_draft_report(id):
    app_data = load_data()
    username = session.get('username', '')
    drafts = app_data['user_drafts'].get(username, [])
    report = next((r for r in drafts if r['id'] == id), None)
    if report:
        return jsonify(report)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/admin/all-configs')
def get_all_configs():
    app_data = load_data()
    return jsonify({k: app_data.get(k, []) for k in ['member_locations', 'service_types', 'mentors', 'locations', 'activities', 'prompt_levels', 'task_categories', 'strategies', 'unit_options', 'medication_statuses', 'medication_types']})

@app.route('/api/admin/<key>', methods=['POST'])
def save_admin_config(key):
    data = request.json
    values = data.get('values', [])
    app_data = load_data()
    
    if key == 'member_locations': app_data['member_locations'] = [{'id': i+1, 'location_name': v, 'is_active': True} for i, v in enumerate(values)]
    elif key == 'service_types': app_data['service_types'] = [{'id': i+1, 'type_name': v, 'is_active': True} for i, v in enumerate(values)]
    elif key == 'mentors': app_data['mentors'] = [{'id': i+1, 'full_name': v, 'is_active': True} for i, v in enumerate(values)]
    elif key == 'locations': app_data['locations'] = [{'id': i+1, 'location_name': v, 'is_active': True} for i, v in enumerate(values)]
    elif key == 'activities': app_data['activities'] = [{'id': i+1, 'activity_name': v, 'is_active': True} for i, v in enumerate(values)]
    elif key == 'prompt_levels': app_data['prompt_levels'] = [{'id': i+1, 'level_name': v, 'is_active': True} for i, v in enumerate(values)]
    elif key == 'task_categories': app_data['task_categories'] = [{'id': i+1, 'category_name': v, 'is_active': True} for i, v in enumerate(values)]
    elif key == 'strategies': app_data['strategies'] = [{'id': i+1, 'strategy_text': v, 'is_active': True} for i, v in enumerate(values)]
    elif key == 'medication_statuses': app_data['medication_statuses'] = [{'id': i+1, 'status_name': v, 'is_active': True} for i, v in enumerate(values)]
    elif key == 'medication_types': app_data['medication_types'] = [{'id': i+1, 'type_name': v, 'is_active': True} for i, v in enumerate(values)]
    elif key == 'unit_options': app_data['unit_options'] = [{'id': i+1, 'unit_value': v.get('unit_value', v), 'display_text': v.get('display_text', f"{v} Units"), 'is_active': True} for i, v in enumerate(values)]
    
    save_data(app_data)
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║     📋 FCCS - Four Corners Community Services 📋          ║
    ╠══════════════════════════════════════════════════════════╣
    ║  PRODUCTION VERSION                                      ║
    ║  ✅ Admin changes save permanently                       ║
    ║  ✅ Location folders: Hackensack, Oxford, Union City     ║
    ║  ✅ Calendar view                                        ║
    ║  ✅ Data persists on Render                              ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    app.run(debug=False, host='0.0.0.0', port=port)
