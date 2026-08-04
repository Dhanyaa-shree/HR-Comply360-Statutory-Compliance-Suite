from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models.document import Document
from models.compliance import Compliance
import os
from datetime import datetime
import mimetypes

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_documents():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        compliance_id = request.args.get('compliance_id', type=int)
        
        query = Document.query
        
        if compliance_id:
            query = query.filter_by(compliance_id=compliance_id)
        
        documents = query.order_by(Document.uploaded_at.desc()).all()
        
        return jsonify([d.to_dict() for d in documents])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/upload', methods=['POST', 'OPTIONS'])
@jwt_required()
def upload_document():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        compliance_id = request.form.get('compliance_id', type=int)
        
        if not compliance_id:
            return jsonify({'error': 'compliance_id is required'}), 400
        
        # Check if compliance exists
        compliance = Compliance.query.get(compliance_id)
        if not compliance:
            return jsonify({'error': 'Compliance not found'}), 404
        
        # Create upload folder if not exists
        os.makedirs('uploads', exist_ok=True)
        
        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Get file type
        file_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'unknown'
        
        # Create document record
        document = Document(
            compliance_id=compliance_id,
            file_name=file.filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<int:id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def download_document(id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        document = Document.query.get_or_404(id)
        
        if not os.path.exists(document.file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.file_name
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<int:id>', methods=['DELETE', 'OPTIONS'])
@jwt_required()
def delete_document(id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        document = Document.query.get_or_404(id)
        
        # Delete file from disk
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete record from database
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'message': 'Document deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<int:id>/preview', methods=['GET', 'OPTIONS'])
@jwt_required()
def preview_document(id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        document = Document.query.get_or_404(id)
        
        if not os.path.exists(document.file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Check if file is image or PDF for preview
        preview_types = ['image', 'pdf']
        file_type = document.file_type or ''
        
        if not any(t in file_type.lower() for t in preview_types):
            return jsonify({'error': 'Preview not available for this file type'}), 400
        
        return send_file(
            document.file_path,
            as_attachment=False,
            download_name=document.file_name
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500