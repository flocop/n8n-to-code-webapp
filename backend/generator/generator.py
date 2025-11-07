"""Main Python code generator"""

from typing import List, Dict, Set
from pathlib import Path
from backend.parser.models import N8nWorkflow, N8nNode
from .node_generators import NodeGeneratorRegistry


class PythonCodeGenerator:
    """Generate Python code from n8n workflows"""

    def __init__(self, workflow: N8nWorkflow):
        self.workflow = workflow
        self.imports: Set[str] = set()
        self.dependencies: Set[str] = set()
        self.functions: List[str] = []

    def generate(self) -> str:
        """
        Generate complete Python code for the workflow.

        Returns:
            Complete Python code as a string
        """
        # Get execution order
        execution_order = self.workflow.get_execution_order()

        # Generate code for each node
        for node_name in execution_order:
            node = self.workflow.get_node_by_name(node_name)
            if node:
                self._generate_node_code(node)

        # Generate main execution function
        main_func = self._generate_main_function(execution_order)

        # Assemble complete code
        code = self._assemble_code(main_func)

        return code

    def _generate_node_code(self, node: N8nNode):
        """Generate code for a single node"""
        generator = NodeGeneratorRegistry.get_generator(node.type)

        if generator:
            result = generator.generate(node)
            self.functions.append(result["code"])
            self.imports.update(result["imports"])
            self.dependencies.update(result["dependencies"])
        else:
            # Generate placeholder for unsupported nodes
            placeholder = self._generate_placeholder(node)
            self.functions.append(placeholder)

    def _generate_placeholder(self, node: N8nNode) -> str:
        """Generate placeholder for unsupported node types"""
        safe_name = self._safe_name(node.name)
        return f'''async def {safe_name}(data):
    """
    Placeholder for unsupported node type: {node.type}
    Node: {node.name}

    This node type is not yet supported by the converter.
    Please implement the logic manually.
    """
    print(f"Warning: Executing placeholder for {node.name}")
    return data  # Pass through data unchanged
'''

    def _generate_main_function(self, execution_order: List[str]) -> str:
        """Generate the main workflow execution function"""
        code = '''async def main():
    """Main workflow execution"""
    print("Starting workflow execution...")

'''

        # Generate execution calls
        for i, node_name in enumerate(execution_order):
            node = self.workflow.get_node_by_name(node_name)
            if not node:
                continue

            safe_name = self._safe_name(node_name)
            inputs = self.workflow.get_node_inputs(node_name)

            # Determine input variable
            if i == 0:
                # First node - no input or uses initial data
                code += f'    print(f"Executing: {node_name}")\n'
                code += f'    {safe_name}_result = await {safe_name}(None)\n\n'
            elif len(inputs) == 0:
                # No inputs (shouldn't happen but handle it)
                code += f'    print(f"Executing: {node_name}")\n'
                code += f'    {safe_name}_result = await {safe_name}(None)\n\n'
            elif len(inputs) == 1:
                # Single input
                prev_node = inputs[0]
                prev_safe_name = self._safe_name(prev_node)
                code += f'    print(f"Executing: {node_name}")\n'
                code += f'    {safe_name}_result = await {safe_name}({prev_safe_name}_result)\n\n'
            else:
                # Multiple inputs - merge them
                input_vars = [f"{self._safe_name(inp)}_result" for inp in inputs]
                code += f'    print(f"Executing: {node_name}")\n'
                code += f'    merged_input = {{}}\n'
                for var in input_vars:
                    code += f'    if isinstance({var}, dict):\n'
                    code += f'        merged_input.update({var})\n'
                code += f'    {safe_name}_result = await {safe_name}(merged_input)\n\n'

        # Add final output
        if execution_order:
            last_node = execution_order[-1]
            last_safe_name = self._safe_name(last_node)
            code += f'    print("\\nWorkflow completed!")\n'
            code += f'    print(f"Final result: {{{last_safe_name}_result}}")\n'
            code += f'    return {last_safe_name}_result\n'
        else:
            code += '    print("No nodes to execute")\n'
            code += '    return None\n'

        return code

    def _assemble_code(self, main_func: str) -> str:
        """Assemble the complete Python code"""
        parts = []

        # Header
        parts.append(f'"""')
        parts.append(f'Generated Python code for n8n workflow: {self.workflow.name}')
        parts.append(f'')
        parts.append(f'This code was automatically generated from an n8n workflow.')
        parts.append(f'You may need to customize it for your specific use case.')
        parts.append(f'"""')
        parts.append('')

        # Imports
        parts.append('import asyncio')
        parts.append('import json')
        if self.imports:
            for imp in sorted(self.imports):
                parts.append(imp)
        parts.append('')
        parts.append('')

        # Node functions
        parts.append('# Node Functions')
        parts.append('# ' + '=' * 70)
        parts.append('')
        for func in self.functions:
            parts.append(func)
            parts.append('')

        # Main function
        parts.append('# Main Workflow')
        parts.append('# ' + '=' * 70)
        parts.append('')
        parts.append(main_func)
        parts.append('')

        # Entry point
        parts.append('')
        parts.append('if __name__ == "__main__":')
        parts.append('    asyncio.run(main())')
        parts.append('')

        return '\n'.join(parts)

    def generate_requirements(self) -> str:
        """Generate requirements.txt content"""
        if not self.dependencies:
            return "# No additional dependencies required\n"

        deps = sorted(self.dependencies)
        return '\n'.join(deps) + '\n'

    def generate_readme(self) -> str:
        """Generate README for the generated code"""
        readme = f'''# {self.workflow.name}

Generated Python code from n8n workflow.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python workflow.py
```

## Nodes

This workflow contains the following nodes:

'''
        for node in self.workflow.nodes:
            readme += f'- **{node.name}** ({node.type})\n'

        readme += '''
## Customization

This code was automatically generated and may need customization:

1. Review placeholder functions and implement missing logic
2. Add error handling as needed
3. Configure authentication and credentials
4. Adjust for your production environment

## Notes

- All functions are async for better performance
- Data flows through the workflow in the order defined by node connections
'''

        return readme

    def _safe_name(self, name: str) -> str:
        """Convert node name to a safe Python variable name"""
        safe = "".join(c if c.isalnum() else "_" for c in name)
        if safe and safe[0].isdigit():
            safe = f"node_{safe}"
        return safe.lower()

    def save_to_directory(self, output_dir: Path):
        """
        Save generated code to a directory.

        Args:
            output_dir: Directory to save files to
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save Python code
        code = self.generate()
        (output_dir / "workflow.py").write_text(code, encoding="utf-8")

        # Save requirements.txt
        requirements = self.generate_requirements()
        (output_dir / "requirements.txt").write_text(requirements, encoding="utf-8")

        # Save README
        readme = self.generate_readme()
        (output_dir / "README.md").write_text(readme, encoding="utf-8")

        print(f"Generated code saved to: {output_dir}")
        print(f"  - workflow.py")
        print(f"  - requirements.txt")
        print(f"  - README.md")
