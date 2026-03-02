{
    "name": "Enterprise Knowledge & Document Management",
    "version": "1.0",
    "summary": "Knowledge Base & Document Management System",
    "description": """
        Enterprise Knowledge Management like Odoo Knowledge.
        Features:
        - Folder Tree
        - Document Editor
        - Version Control
        - Workflow
        - Permission
    """,
    "category": "Productivity",
    "author": "Your Company",
    "depends": ["base", "mail", "web"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequences.xml",
        "views/menu.xml",
        "views/folder_views.xml",
        "views/document_views.xml",
        "views/tag_views.xml"
    ],
    "installable": True,
    "application": True,
}