from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db



class DocumentationModel(db.Model):

    __tablename__ = 'documentations'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    swagger = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_json(self):
        return {
            'uuid': self.uuid,
            'service_id': self.service_id,
            'swagger': self.swagger,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    @staticmethod
    def create(service, new_documentation):
        documentantion = DocumentationModel(**new_documentation)
        documentantion.service_id = service.id

        db.session.add(documentantion)
        db.session.commit()

        return documentantion


    @staticmethod
    def get_by_uuid(uuid):
        return DocumentationModel.query.filter_by(uuid=uuid).first()



    @staticmethod
    def get_by_service_id(service_id):
        return DocumentationModel.query.filter_by(service_id=service_id).first()



    @staticmethod
    def update(documentation, new_documentation):
        for key, value in new_documentation.items():
            setattr(documentation, key, value)

        db.session.commit()

        return documentation
