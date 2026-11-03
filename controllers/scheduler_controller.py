from flask import Blueprint, jsonify
from utils.decorators import country_scope
from models.user import SUPER_ADMIN
import app

scheduler_bp = Blueprint('scheduler', __name__)

@scheduler_bp.route('/trigger-check', methods=['POST'])
@country_scope(roles=[SUPER_ADMIN])
def trigger_check(country_id):
    """Manually trigger the daily receipt check (Admin only)"""
    try:
        if app.scheduler_service:
            app.scheduler_service.trigger_check_now()
            return jsonify({
                'status': True,
                'message': 'Daily receipt check triggered successfully'
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': 'Scheduler service not initialized'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Failed to trigger check: {str(e)}'
        }), 500

@scheduler_bp.route('/status', methods=['GET'])
@country_scope(roles=[SUPER_ADMIN])
def get_status(country_id):
    """Get scheduler status (Admin only)"""
    try:
        if app.scheduler_service:
            is_running = app.scheduler_service.scheduler.running
            jobs = []
            
            for job in app.scheduler_service.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                })
            
            return jsonify({
                'status': True,
                'data': {
                    'running': is_running,
                    'recipients': app.scheduler_service.alert_recipients,
                    'check_days': app.scheduler_service.check_days,
                    'check_time': f"{app.scheduler_service.check_hour:02d}:{app.scheduler_service.check_minute:02d}",
                    'jobs': jobs
                }
            }), 200
        else:
            return jsonify({
                'status': False,
                'message': 'Scheduler service not initialized'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Failed to get scheduler status: {str(e)}'
        }), 500