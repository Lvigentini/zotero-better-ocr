var mainMenu;

function startup({ id, version, rootURI }) {
	Zotero.debug("Better OCR: Starting up (v" + version + ")");
	addToAllWindows();
}

function shutdown() {
	removeFromAllWindows();
}

function install() {}
function uninstall() {}

function addToWindow(win) {
	let doc = win.document;
	let menu = doc.getElementById('zotero-itemmenu');
	
    if (!menu) {
        Zotero.debug("Better OCR: zotero-itemmenu not found in window");
        return;
    }

    // CLEANUP: Remove any existing item first (duplicates safety)
    let existing = doc.getElementById('better-ocr-menu-item');
    if (existing) existing.remove();

    // CREATE ELEMENT (Zotero 7 / XUL Compatible)
    // Zotero 7 uses XHTML/XUL hybrid. 'createXULElement' is the safest way for UI widgets.
    let menuItem;
    if (doc.createXULElement) {
        menuItem = doc.createXULElement('menuitem');
    } else {
        // Fallback for older Zotero or standard DOM
        menuItem = doc.createElementNS('http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul', 'menuitem');
    }

	menuItem.setAttribute('id', 'better-ocr-menu-item');
	menuItem.setAttribute('label', 'Extract Text (Better OCR)');
	menuItem.setAttribute('class', 'menuitem-iconic');
    // menuItem.setAttribute('image', rootURI + 'icon.png'); // Icon optional

	menuItem.addEventListener('command', performOCR, false);
	
	menu.appendChild(menuItem);
    Zotero.debug("Better OCR: Menu item added");
	mainMenu = menuItem;
}

function addToAllWindows() {
	let windows = Zotero.getMainWindows();
	for (let win of windows) {
		addToWindow(win);
	}
}

function removeFromAllWindows() {
	let windows = Zotero.getMainWindows();
	for (let win of windows) {
		let doc = win.document;
		let menuItem = doc.getElementById('better-ocr-menu-item');
		if (menuItem) menuItem.remove();
	}
}

var windowListener = {
	onOpenWindow: function (xulWin) {
		let win = xulWin.QueryInterface(Components.interfaces.nsIInterfaceRequestor)
						.getInterface(Components.interfaces.nsIDOMWindow);
		win.addEventListener("load", function () {
			win.removeEventListener("load", arguments.callee, false);
			addToWindow(win);
		}, false);
	},
	onCloseWindow: function (xulWin) {},
	onWindowTitleChange: function (xulWin, newTitle) {}
};

async function performOCR() {
	var items = Zotero.getActiveZoteroPane().getSelectedItems();
    if (!items.length) return;

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

    if (pdfItems.length === 0) {
        alert("Better OCR: No PDF attachments found for the selected item(s).");
        return;
    }

	Zotero.showZoteroPaneProgressMeter("Running Better OCR...");
	try {
		for (let attachmentItem of pdfItems) {
			await processItem(attachmentItem);
		}
	} catch (e) {
		Zotero.logError(e);
		alert("Error during OCR: " + e);
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
        let addon = Zotero.getInstalledExtensions().find(x => x.id == "better-ocr@lvigentini");
        if (!addon) return reject("Plugin ID not found!"); 
        
        let exeFile = addon.rootDir.clone(); 
        exeFile.append("bin");
        
        var xulRuntime = Components.classes["@mozilla.org/xre/app-info;1"]
                           .getService(Components.interfaces.nsIXULRuntime);
        
        if (xulRuntime.OS == "WINNT") {
            exeFile.append("BetterOCR_Tool.exe");
        } else {
            exeFile.append("BetterOCR_Tool");
        }

        if (!exeFile.exists()) {
            return reject("Embedded Engine not found at: " + exeFile.path);
        }
        
        if (xulRuntime.OS != "WINNT") {
            try { exeFile.permissions |= 0o755; } catch(e) {}
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
