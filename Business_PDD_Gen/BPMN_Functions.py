# BPMN-Functions
# Function to generate the HTML and JavaScript for BPMN Viewer

from App_Logger import get_logger
logger = get_logger()

def render_bpmn_viewer(bpmn_xml):
    """
    Render the BPMN viewer with the provided XML content and add an export to PNG feature.

    :param bpmn_xml: str: BPMN XML content to display in the viewer.
    """
    try:
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <!-- Required viewer styles -->
            <link rel="stylesheet" href="https://unpkg.com/bpmn-js@18.1.2/dist/assets/bpmn-js.css" />
        </head>
        <body>
            <div id="canvas" style="width: 100%; height: 800px; border: 1px solid #ccc;"></div>
            <button id="export-png" style="margin-top: 10px;">Export as PNG</button>

            <!-- BPMN Viewer library -->
            <script src="https://unpkg.com/bpmn-js@18.1.2/dist/bpmn-viewer.development.js"></script>
            <script>
                const bpmnJS = new BpmnJS({{ container: '#canvas' }});

                const bpmnDiagram = `{bpmn_xml}`;

                bpmnJS.importXML(bpmnDiagram).then(() => {{
                    console.log('BPMN Diagram successfully rendered!');
                    bpmnJS.get('canvas').zoom('fit-viewport', 'auto');
                }}).catch((err) => {{
                    console.error('Error rendering BPMN Diagram:', err);
                }});

                // Add event listener for the export button
                const exportButton = document.getElementById('export-png');
                if (exportButton) {{
                    exportButton.addEventListener('click', () => {{
                        console.log('Export button clicked!');
                        bpmnJS.savePNG((err, png) => {{
                            if (err) {{
                                console.error('Error exporting PNG:', err);
                                return;
                            }}

                            // Create a download link for the PNG
                            const link = document.createElement('a');
                            link.href = png;
                            link.download = 'bpmn_diagram.png';
                            document.body.appendChild(link); // Required for Firefox
                            link.click();
                            document.body.removeChild(link); // Clean up
                        }});
                    }});
                }} else {{
                    console.error('Export button not found!');
                }}
            </script>
        </body>
        </html>
        """
        logger.info("BPMN file is rendered successfully")
    except Exception as e:
        logger.error(f"Error rendering BPMN Diagram: {e}")
        return f"Error rendering BPMN Diagram: {e}"

    return html_code