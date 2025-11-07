"""Command-line interface for n8n to Python converter"""

import sys
import click
from pathlib import Path
from backend.parser import WorkflowParser
from backend.generator import PythonCodeGenerator


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """n8n to Python Code Converter CLI

    Convert n8n workflows to production-ready Python code.
    """
    pass


@cli.command()
@click.argument("workflow_file", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: workflow.py)",
)
@click.option(
    "--output-dir",
    "-d",
    type=click.Path(),
    help="Output directory for all generated files",
)
@click.option(
    "--validate",
    "-v",
    is_flag=True,
    help="Validate workflow before converting",
)
def convert(workflow_file, output, output_dir, validate):
    """Convert an n8n workflow JSON file to Python code"""

    click.echo(f"📄 Reading workflow from: {workflow_file}")

    try:
        # Parse the workflow
        workflow = WorkflowParser.parse_file(workflow_file)
        click.echo(f"✅ Successfully parsed workflow: {workflow.name}")
        click.echo(f"   Nodes: {len(workflow.nodes)}")

        # Validate if requested
        if validate:
            click.echo("\n🔍 Validating workflow...")
            is_valid, errors = WorkflowParser.validate_workflow(workflow)

            if is_valid:
                click.echo("✅ Workflow is valid!")
            else:
                click.echo("⚠️  Workflow has validation warnings:")
                for error in errors:
                    click.echo(f"   - {error}")
                click.echo()

        # Generate code
        click.echo("\n🔄 Generating Python code...")
        generator = PythonCodeGenerator(workflow)

        if output_dir:
            # Save to directory with all files
            output_path = Path(output_dir)
            generator.save_to_directory(output_path)
            click.echo(f"\n✅ Code generated successfully!")
            click.echo(f"📁 Output directory: {output_path}")
        else:
            # Just save the Python file
            code = generator.generate()
            output_path = Path(output) if output else Path("workflow.py")
            output_path.write_text(code, encoding="utf-8")
            click.echo(f"\n✅ Code generated successfully!")
            click.echo(f"📄 Output file: {output_path}")

        # Show supported/unsupported nodes
        click.echo("\n📊 Node Support Summary:")
        from backend.generator import NodeGeneratorRegistry

        supported = []
        unsupported = []

        for node in workflow.nodes:
            generator_obj = NodeGeneratorRegistry.get_generator(node.type)
            if generator_obj:
                supported.append(node.name)
            else:
                unsupported.append((node.name, node.type))

        click.echo(f"   ✅ Supported nodes: {len(supported)}")
        for name in supported:
            click.echo(f"      - {name}")

        if unsupported:
            click.echo(f"   ⚠️  Unsupported nodes: {len(unsupported)} (placeholders generated)")
            for name, node_type in unsupported:
                click.echo(f"      - {name} ({node_type})")

        click.echo("\n🎉 Done! You can now run the generated code.")

    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument("workflow_file", type=click.Path(exists=True))
def validate(workflow_file):
    """Validate an n8n workflow JSON file"""

    click.echo(f"📄 Reading workflow from: {workflow_file}")

    try:
        # Parse the workflow
        workflow = WorkflowParser.parse_file(workflow_file)
        click.echo(f"✅ Successfully parsed workflow: {workflow.name}")
        click.echo(f"   Nodes: {len(workflow.nodes)}")
        click.echo(f"   Connections: {len(workflow.connections)}")

        # Validate
        click.echo("\n🔍 Validating workflow...")
        is_valid, errors = WorkflowParser.validate_workflow(workflow)

        if is_valid:
            click.echo("\n✅ Workflow is valid!")

            # Show execution order
            click.echo("\n📋 Execution Order:")
            order = workflow.get_execution_order()
            for i, node_name in enumerate(order, 1):
                node = workflow.get_node_by_name(node_name)
                click.echo(f"   {i}. {node_name} ({node.type if node else 'unknown'})")

        else:
            click.echo("\n❌ Workflow has errors:")
            for error in errors:
                click.echo(f"   - {error}")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def supported():
    """List supported n8n node types"""

    from backend.generator import NodeGeneratorRegistry

    click.echo("📋 Supported n8n Node Types:\n")

    types = NodeGeneratorRegistry.get_supported_types()

    # Group by category
    categories = {
        "Core": [],
        "Triggers": [],
        "Actions": [],
        "Logic": [],
    }

    for node_type in sorted(types):
        if "trigger" in node_type.lower() or "webhook" in node_type.lower():
            categories["Triggers"].append(node_type)
        elif "if" in node_type.lower() or "switch" in node_type.lower():
            categories["Logic"].append(node_type)
        elif "http" in node_type.lower() or "request" in node_type.lower():
            categories["Actions"].append(node_type)
        else:
            categories["Core"].append(node_type)

    for category, types_list in categories.items():
        if types_list:
            click.echo(f"\n{category}:")
            for node_type in types_list:
                click.echo(f"  ✅ {node_type}")

    click.echo(f"\n📊 Total: {len(types)} node types supported")
    click.echo("\n💡 More node types will be added in future updates!")


if __name__ == "__main__":
    cli()
