# Upload Notifier
Dieses Paket sendet beim Scoren einen POST-Request mit LMS-Attributen als JSON formatiert an
eine in den Options einstellbaren Endpoint.

## Request-Format

### Einzelabgabe
```json
{
  "lms": {
    "course_id": "2",
    "submission_id": 6,
    "module_instance": 5
  },
  "user": {
    "user_id": "3"
  },
  "group": null
}
```

### Gruppenabgabe
```json
{
  "lms": {
    "course_id": "2",
    "submission_id": 8,
    "module_instance": 5
  },
  "user": null,
  "group": {
    "group_id": 1,
    "members": [
      {
        "user_id": "3"
      },
      {
        "user_id": "2"
      }
    ]
  }
}
```

## Voraussetzungen

### Endpoint
Aktuell muss der Endpoint per Basic-Auth gesichert sein. Die Zugangsdaten können in den Options angegeben werden.

### QuestionPy-Server
Damit alle Attribute an die URL gesendet werden können, müssen diese in der `config.yml` des QuestionPy-Servers
freigegeben werden, z.B. mit:
```yaml
permissions:
  auto_grant_permissions:
    lms_attributes:
      - user_id
      - group_id
      - course_id
      - attempt_id
      - lms_moodle_assignment_submission_id
      - lms_moodle_module_instance
```
