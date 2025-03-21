import os
import uuid
from datetime import datetime
import logging

from flask import request, jsonify, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import base64

from app import app, db
from models import Analysis
from image_processor import ThreadCounter

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload from web interface"""
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['file']
    
    # If user does not select file, browser might submit an empty file without filename
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to prevent collisions
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{unique_id}.{extension}"
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Create a new analysis record in the database
        new_analysis = Analysis(
            filename=unique_filename,
            original_filename=original_filename,
            image_processed=False
        )
        db.session.add(new_analysis)
        db.session.commit()
        
        # Process the image
        try:
            measurement_unit = request.form.get('unit', 'cm')
            reference_length = float(request.form.get('reference_length', 1.0))
            
            # Initialize thread counter with the selected unit and reference length
            counter = ThreadCounter(unit=measurement_unit, reference_length=reference_length)
            
            # Analyze the image
            results = counter.count_threads(file_path)
            
            # Update the analysis record with the results
            new_analysis.warp_count = results['warp_count']
            new_analysis.weft_count = results['weft_count']
            new_analysis.thread_density = results['thread_density']
            new_analysis.confidence_score = results['confidence_score']
            new_analysis.measurement_unit = measurement_unit
            new_analysis.notes = request.form.get('notes', '')
            new_analysis.image_processed = True
            db.session.commit()
            
            # If this was called from the web interface, redirect to results page
            if request.form.get('source') == 'web':
                return redirect(url_for('view_result', analysis_id=new_analysis.id))
            
            # Otherwise return JSON result for API clients
            return jsonify({
                'success': True,
                'analysis_id': new_analysis.id,
                'results': results
            })
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            db.session.delete(new_analysis)
            db.session.commit()
            
            if request.form.get('source') == 'web':
                flash(f'Error processing image: {str(e)}', 'danger')
                return redirect(url_for('index'))
            
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # If file extension not allowed
    flash('File type not allowed. Please upload a valid image file.', 'danger')
    return redirect(request.url)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for image analysis from mobile app"""
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser might submit an empty file without filename
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to prevent collisions
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{unique_id}.{extension}"
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Create a new analysis record in the database
        new_analysis = Analysis(
            filename=unique_filename,
            original_filename=original_filename,
            image_processed=False
        )
        db.session.add(new_analysis)
        db.session.commit()
        
        # Process the image
        try:
            measurement_unit = request.form.get('unit', 'cm')
            reference_length = float(request.form.get('reference_length', 1.0))
            
            # Initialize thread counter with the selected unit and reference length
            counter = ThreadCounter(unit=measurement_unit, reference_length=reference_length)
            
            # Analyze the image
            results = counter.count_threads(file_path)
            
            # Update the analysis record with the results
            new_analysis.warp_count = results['warp_count']
            new_analysis.weft_count = results['weft_count']
            new_analysis.thread_density = results['thread_density']
            new_analysis.confidence_score = results['confidence_score']
            new_analysis.measurement_unit = measurement_unit
            new_analysis.notes = request.form.get('notes', '')
            new_analysis.image_processed = True
            db.session.commit()
            
            # Return detailed results to the mobile app
            return jsonify({
                'success': True,
                'analysis_id': new_analysis.id,
                'results': {
                    'warp_count': results['warp_count'],
                    'weft_count': results['weft_count'],
                    'thread_density': results['thread_density'],
                    'confidence_score': results['confidence_score'],
                    'measurement_unit': measurement_unit,
                    'visual_result': results['visual_result']
                }
            })
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            db.session.delete(new_analysis)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # If file extension not allowed
    return jsonify({
        'success': False, 
        'error': 'File type not allowed. Please upload a valid image file.'
    }), 400

@app.route('/result/<int:analysis_id>')
def view_result(analysis_id):
    """View the results of a specific analysis"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Check if the image was processed successfully
    if not analysis.image_processed:
        flash('Image has not been processed yet.', 'warning')
        return redirect(url_for('index'))
    
    # Get the file path for visualization
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], analysis.filename)
    
    # Re-process the image to get visualization
    try:
        counter = ThreadCounter(unit=analysis.measurement_unit)
        results = counter.count_threads(file_path)
        
        # Get the visualization as base64
        visualization = results['visual_result']
        
        return render_template(
            'results.html', 
            analysis=analysis, 
            visualization=visualization
        )
    
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        flash(f'Error generating visualization: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/history')
def history():
    """View history of previous analyses"""
    analyses = Analysis.query.filter_by(image_processed=True).order_by(Analysis.date_created.desc()).all()
    return render_template('history.html', analyses=analyses)

@app.route('/api/history')
def api_history():
    """API endpoint to get history of analyses for mobile app"""
    analyses = Analysis.query.filter_by(image_processed=True).order_by(Analysis.date_created.desc()).all()
    results = [analysis.to_dict() for analysis in analyses]
    
    return jsonify({
        'success': True,
        'count': len(results),
        'analyses': results
    })

@app.route('/api/result/<int:analysis_id>')
def api_result(analysis_id):
    """API endpoint to get a specific analysis result for mobile app"""
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Check if the image was processed successfully
    if not analysis.image_processed:
        return jsonify({
            'success': False,
            'error': 'Image has not been processed yet.'
        }), 400
    
    # Get the file path for visualization
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], analysis.filename)
    
    # Re-process the image to get visualization
    try:
        counter = ThreadCounter(unit=analysis.measurement_unit)
        results = counter.count_threads(file_path)
        
        # Return the detailed result for the mobile app
        return jsonify({
            'success': True,
            'analysis': analysis.to_dict(),
            'visualization': results['visual_result']
        })
    
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error generating visualization: {str(e)}'
        }), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500
