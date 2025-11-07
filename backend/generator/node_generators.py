"""Node-specific code generators"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from backend.parser.models import N8nNode


class NodeGenerator(ABC):
    """Base class for node-specific code generators"""

    @abstractmethod
    def generate(self, node: N8nNode, input_var: str = "data") -> Dict[str, Any]:
        """
        Generate code for a specific node.

        Args:
            node: The n8n node to generate code for
            input_var: The variable name containing input data

        Returns:
            Dictionary with:
            - code: The generated Python code
            - imports: List of required imports
            - dependencies: List of pip packages needed
        """
        pass

    def _safe_name(self, name: str) -> str:
        """Convert node name to a safe Python variable name"""
        # Replace spaces and special chars with underscores
        safe = "".join(c if c.isalnum() else "_" for c in name)
        # Ensure it doesn't start with a number
        if safe and safe[0].isdigit():
            safe = f"node_{safe}"
        return safe.lower()


class HttpRequestGenerator(NodeGenerator):
    """Generator for HTTP Request nodes"""

    def generate(self, node: N8nNode, input_var: str = "data") -> Dict[str, Any]:
        params = node.parameters
        method = params.get("method", "GET").upper()
        url = params.get("url", "")

        # Handle authentication
        auth_type = params.get("authentication", "none")
        auth_code = ""

        # Request options
        headers = params.get("headerParameters", {}).get("parameters", []) if isinstance(params.get("headerParameters"), dict) else []
        query_params = params.get("queryParameters", {}).get("parameters", []) if isinstance(params.get("queryParameters"), dict) else []
        body_params = params.get("body", "")

        # Build headers dict
        headers_code = "headers = {\n"
        for header in headers:
            if isinstance(header, dict):
                name = header.get("name", "")
                value = header.get("value", "")
                headers_code += f'        "{name}": "{value}",\n'
        headers_code += "    }"

        # Build query params dict
        params_code = "params = {\n"
        for param in query_params:
            if isinstance(param, dict):
                name = param.get("name", "")
                value = param.get("value", "")
                params_code += f'        "{name}": "{value}",\n'
        params_code += "    }"

        # Generate the code
        code = f'''async def {self._safe_name(node.name)}({input_var}):
    """HTTP Request: {node.name}"""
    {headers_code}
    {params_code}

    async with httpx.AsyncClient() as client:
        response = await client.{method.lower()}(
            "{url}",
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        return response.json()
'''

        return {
            "code": code,
            "imports": ["import httpx"],
            "dependencies": ["httpx>=0.26.0"],
        }


class CodeNodeGenerator(NodeGenerator):
    """Generator for Code/Function nodes"""

    def generate(self, node: N8nNode, input_var: str = "data") -> Dict[str, Any]:
        params = node.parameters

        # Get the JavaScript code (we'll need to convert or note it)
        js_code = params.get("jsCode", params.get("functionCode", ""))

        # For now, we'll create a placeholder that user needs to fill
        code = f'''async def {self._safe_name(node.name)}({input_var}):
    """Code Node: {node.name}

    Original n8n code (JavaScript):
    {js_code[:200]}...

    TODO: Convert the above JavaScript logic to Python
    """
    # Implement your custom logic here
    result = {input_var}  # Placeholder

    return result
'''

        return {
            "code": code,
            "imports": [],
            "dependencies": [],
        }


class IfNodeGenerator(NodeGenerator):
    """Generator for IF nodes"""

    def generate(self, node: N8nNode, input_var: str = "data") -> Dict[str, Any]:
        params = node.parameters

        # Get conditions
        conditions = params.get("conditions", {})
        condition_type = conditions.get("conditions", [])

        # Build condition code
        condition_code = "# TODO: Implement condition logic\n    condition_met = True  # Placeholder"

        if condition_type:
            # Try to parse the condition
            try:
                first_condition = condition_type[0] if condition_type else {}
                field = first_condition.get("leftValue", "")
                operation = first_condition.get("operation", "")
                value = first_condition.get("rightValue", "")

                op_map = {
                    "equal": "==",
                    "notEqual": "!=",
                    "larger": ">",
                    "largerEqual": ">=",
                    "smaller": "<",
                    "smallerEqual": "<=",
                    "contains": "in",
                }

                py_op = op_map.get(operation, "==")
                condition_code = f'condition_met = {input_var}.get("{field}") {py_op} "{value}"'
            except:
                pass

        code = f'''async def {self._safe_name(node.name)}({input_var}):
    """IF Node: {node.name}"""
    {condition_code}

    if condition_met:
        return ("true", {input_var})
    else:
        return ("false", {input_var})
'''

        return {
            "code": code,
            "imports": [],
            "dependencies": [],
        }


class SetNodeGenerator(NodeGenerator):
    """Generator for Set nodes (variable assignment)"""

    def generate(self, node: N8nNode, input_var: str = "data") -> Dict[str, Any]:
        params = node.parameters

        # Get the values to set
        values = params.get("values", {})

        code = f'''async def {self._safe_name(node.name)}({input_var}):
    """Set Node: {node.name}"""
    result = {input_var}.copy() if isinstance({input_var}, dict) else {{}}

    # Set new values
'''

        # Add value assignments
        if isinstance(values, dict):
            for key, value in values.items():
                code += f'    result["{key}"] = "{value}"\n'

        code += "    \n    return result\n"

        return {
            "code": code,
            "imports": [],
            "dependencies": [],
        }


class WebhookTriggerGenerator(NodeGenerator):
    """Generator for Webhook trigger nodes"""

    def generate(self, node: N8nNode, input_var: str = "data") -> Dict[str, Any]:
        params = node.parameters
        path = params.get("path", "/webhook")
        method = params.get("httpMethod", "POST")

        code = f'''async def {self._safe_name(node.name)}({input_var}=None):
    """Webhook Trigger: {node.name}

    Path: {path}
    Method: {method}

    This would be triggered by an HTTP request in production.
    For testing, we'll use sample data.
    """
    if {input_var} is None:
        # Sample data for testing
        {input_var} = {{"message": "Hello from webhook"}}

    return {input_var}
'''

        return {
            "code": code,
            "imports": [],
            "dependencies": [],
        }


class NodeGeneratorRegistry:
    """Registry for node generators"""

    _generators: Dict[str, NodeGenerator] = {}

    @classmethod
    def register(cls, node_type: str, generator: NodeGenerator):
        """Register a generator for a node type"""
        cls._generators[node_type] = generator

    @classmethod
    def get_generator(cls, node_type: str) -> Optional[NodeGenerator]:
        """Get generator for a node type"""
        # Try exact match first
        if node_type in cls._generators:
            return cls._generators[node_type]

        # Try partial matches
        for registered_type, generator in cls._generators.items():
            if registered_type.lower() in node_type.lower():
                return generator

        return None

    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of supported node types"""
        return list(cls._generators.keys())


# Register built-in generators
NodeGeneratorRegistry.register("n8n-nodes-base.httpRequest", HttpRequestGenerator())
NodeGeneratorRegistry.register("n8n-nodes-base.code", CodeNodeGenerator())
NodeGeneratorRegistry.register("n8n-nodes-base.function", CodeNodeGenerator())
NodeGeneratorRegistry.register("n8n-nodes-base.if", IfNodeGenerator())
NodeGeneratorRegistry.register("n8n-nodes-base.set", SetNodeGenerator())
NodeGeneratorRegistry.register("n8n-nodes-base.webhook", WebhookTriggerGenerator())

# Common aliases
NodeGeneratorRegistry.register("httpRequest", HttpRequestGenerator())
NodeGeneratorRegistry.register("code", CodeNodeGenerator())
NodeGeneratorRegistry.register("if", IfNodeGenerator())
NodeGeneratorRegistry.register("set", SetNodeGenerator())
NodeGeneratorRegistry.register("webhook", WebhookTriggerGenerator())
