/**
 * I load pyodide and pygpod
 * 
 * passes off actions to ipod_operations.py
 */

const PYODIDE_VERSION = "0.26.4";
const PYODIDE_BASE = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
const bootstrapScript = document.querySelector('script[data-app-py]');


let pyodide = null;


function setEngineStatus(text) {

    const el = document.getElementById("pyodide-status");

    if (el) el.textContent= text;
}

function setConnectEnabled(enabled) {

    const btn = document.getElementById("connect-ipod");
    if (btn) btn.disabled = !enabled;
}

async function loadIpodApp(appPyUrl) {

    const res = await fetch(appPyUrl);

    if (!res.ok) {
        throw new Error(`Could not load ipod_operations.py (${res.status})`);
    }

    const source = await res.text();

    pyodide.FS.writeFile("/ipod_operations.py", source);

    pyodide.globals.set("pyodide", pyodide);
    await pyodide.runPythonAsync(`

        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("ipod_operations", "/ipod_operations.py")

        ipod_operations = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(ipod_operations)

        sys.modules["ipod_operations"] = ipod_operations

        await ipod_operations.main(pyodide)
    `);
}

async function init() {

    const appPyUrl = bootstrapScript?.dataset?.appPy;
    const pygpodWheelUrl = bootstrapScript?.dataset?.pygpodWheel;

    if (!appPyUrl || !pygpodWheelUrl) {
        setEngineStatus("Missing ipod_operations.py URL :( Where did it go?")
        return;
    }

    setConnectEnabled(false);
    setEngineStatus("Loading pyodide and pygpod engine. Vroooooom Vroooom. wow its loud.")

    try {

        const { loadPyodide } = await import(`${PYODIDE_BASE}pyodide.mjs`)

        pyodide = await loadPyodide({ indexURL: PYODIDE_BASE });

        await pyodide.loadPackage("micropip");

        pyodide.globals.set("pygpod_wheel_url", pygpodWheelUrl);
        await pyodide.runPythonAsync(`
            import micropip
            await micropip.install(pygpod_wheel_url)
        `);

        await loadIpodApp(appPyUrl);

        setEngineStatus("pyodide + pygpod finished loading")
        setConnectEnabled(true);

        document.getElementById("connect-ipod")?.addEventListener("click", async () => {

            setConnectEnabled(false);

            try {
                await pyodide.runPythonAsync("await ipod_operations.connect_ipod()");
            } finally {
                setConnectEnabled(true);
            }
        });
    } catch (err) {

        console.error(err);

        setEngineStatus("Failed to load iPod engine");

        setConnectEnabled(false);
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}