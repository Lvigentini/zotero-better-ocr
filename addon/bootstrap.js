var mainMenu;

function startup({ id, version, rootURI }) {
	Zotero.debug("Better OCR: Starting up");
	
	let win = Zotero.getMainWindow();
	if (win && win.document) {
		let menu = win.document.getElementById('zotero-itemmenu');
		if (menu) {
			let menuItem = win.document.createElement('menuitem');
			menuItem.setAttribute('id', 'better-ocr-menu-item');
			menuItem.setAttribute('label', 'Extract Text (Better OCR)');
			menuItem.addEventListener('command', performOCR, false);
			menu.appendChild(menuItem);
			mainMenu = menuItem;
		}
	}
}

function shutdown() {
	if (mainMenu) mainMenu.remove();
}

function install() {}
function uninstall() {}

async function performOCR() {
	var items = Zotero.getActiveZoteroPane().getSelectedItems();
    let pdfItems = [];
	for (let item of items) {
		if (item.isAttachment() && item.attachmentContentType == 'application/pdf') {
			pdfItems.push(item);
		} else if (item.isRegularItem()) {
			let attachment = await item.getBestAttachment();
			if (attachment && attachment.attachmentContentType == 'application/pdf') {
				pdfItems.push(attachment);
			}
		}
	}
    if (pdfItems.length === 0) return alert("No PDFs selected.");

	Zotero.showZoteroPaneProgressMeter("Running Embedded OCR...");
	try {
		for (let attachmentItem of pdfItems) {
			await processItem(attachmentItem);
		}
	} catch (e) {
		Zotero.logError(e);
		alert("Error: " + e);
	} finally {
		Zotero.hideZoteroPaneProgressMeter();
	}
}

async function processItem(attachmentItem) {
	let pdfPath = await attachmentItem.getFilePathAsync();
	if (!pdfPath) return;

	try {
		await runBundledExecutable(pdfPath);
		
		let txtPath = pdfPath.substring(0, pdfPath.lastIndexOf('.')) + ".txt";
		
		if (await IOUtils.exists(txtPath)) {
			let content = await IOUtils.readUTF8(txtPath);
			let parentItem = Zotero.Items.get(attachmentItem.parentID);
			let targetID = parentItem ? parentItem.id : attachmentItem.id;
			
			let note = new Zotero.Item('note');
			note.parentID = targetID;
			let cleanText = content.replace(/</g, "&lt;").replace(/>/g, "&gt;");
			note.setNote(`<h1>OCR Extraction</h1><p>Source: ${attachmentItem.getField('title')}</p><pre>${cleanText}</pre>`);
			await note.saveTx();
			
			await IOUtils.remove(txtPath);
		}
	} catch (e) {
		throw e;
	}
}

function runBundledExecutable(pdfPath) {
	return new Promise((resolve, reject) => {
        let addon = Zotero.getInstalledExtensions().find(x => x.id == "better-ocr@gemini.user");
        if (!addon) return reject("Plugin ID not found!"); 
        
        let exeFile = addon.rootDir.clone(); 
        exeFile.append("bin");
        
        // Detect OS and choose binary name
        var xulRuntime = Components.classes["@mozilla.org/xre/app-info;1"]
                           .getService(Components.interfaces.nsIXULRuntime);
        
        if (xulRuntime.OS == "WINNT") {
            exeFile.append("BetterOCR_Tool.exe");
        } else {
            // Mac (Darwin) or Linux
            exeFile.append("BetterOCR_Tool");
        }

        if (!exeFile.exists()) {
            return reject("Embedded Engine not found at: " + exeFile.path);
        }
        
        // On Mac/Linux, we might need to ensure execution permissions
        if (xulRuntime.OS != "WINNT") {
            try {
                exeFile.permissions |= 0o755;
            } catch(e) { Zotero.debug("Could not set permissions: " + e); }
        }

		let process = Components.classes["@mozilla.org/process/util;1"]
					.createInstance(Components.interfaces.nsIProcess);
		process.init(exeFile);
		let args = [pdfPath];

		process.runAsync(args, args.length, {
			observe: function(subject, topic, data) {
				if (topic === "process-finished") resolve();
				else reject("Engine execution failed.");
			}
		});
	});
}