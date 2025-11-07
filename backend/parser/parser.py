"""Parser for n8n workflow JSON files"""

import json
from pathlib import Path
from typing import Union
from pydantic import ValidationError
from .models import N8nWorkflow


class WorkflowParser:
    """Parse n8n workflow JSON into structured models"""

    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> N8nWorkflow:
        """
        Parse an n8n workflow from a JSON file.

        Args:
            file_path: Path to the n8n workflow JSON file

        Returns:
            Parsed N8nWorkflow object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValidationError: If JSON structure is invalid
            json.JSONDecodeError: If file is not valid JSON
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Workflow file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return WorkflowParser.parse_dict(data)

    @staticmethod
    def parse_string(json_string: str) -> N8nWorkflow:
        """
        Parse an n8n workflow from a JSON string.

        Args:
            json_string: JSON string containing the workflow

        Returns:
            Parsed N8nWorkflow object

        Raises:
            ValidationError: If JSON structure is invalid
            json.JSONDecodeError: If string is not valid JSON
        """
        data = json.loads(json_string)
        return WorkflowParser.parse_dict(data)

    @staticmethod
    def parse_dict(data: dict) -> N8nWorkflow:
        """
        Parse an n8n workflow from a dictionary.

        Args:
            data: Dictionary containing the workflow data

        Returns:
            Parsed N8nWorkflow object

        Raises:
            ValidationError: If structure is invalid
        """
        try:
            workflow = N8nWorkflow(**data)
            return workflow
        except ValidationError as e:
            raise ValidationError(f"Invalid n8n workflow structure: {e}")

    @staticmethod
    def validate_workflow(workflow: N8nWorkflow) -> tuple[bool, list[str]]:
        """
        Validate a workflow for common issues.

        Args:
            workflow: The workflow to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check if workflow has nodes
        if not workflow.nodes:
            errors.append("Workflow has no nodes")

        # Check for duplicate node names
        node_names = [node.name for node in workflow.nodes]
        duplicates = set([name for name in node_names if node_names.count(name) > 1])
        if duplicates:
            errors.append(f"Duplicate node names found: {', '.join(duplicates)}")

        # Check if connections reference valid nodes
        valid_names = set(node_names)
        for source_name, connection_map in workflow.connections.items():
            if source_name not in valid_names:
                errors.append(f"Connection source '{source_name}' is not a valid node")

            if connection_map.main:
                for connection_list in connection_map.main:
                    for conn in connection_list:
                        if conn.node not in valid_names:
                            errors.append(
                                f"Connection target '{conn.node}' from '{source_name}' is not a valid node"
                            )

        # Check for isolated nodes (no connections in or out)
        for node in workflow.nodes:
            # Skip trigger nodes (they typically have no inputs)
            if "trigger" in node.type.lower():
                continue

            inputs = workflow.get_node_inputs(node.name)
            outputs = workflow.get_node_outputs(node.name)

            if not inputs and not outputs:
                errors.append(f"Node '{node.name}' is isolated (no connections)")

        is_valid = len(errors) == 0
        return is_valid, errors
