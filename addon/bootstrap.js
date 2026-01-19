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
	
    if (!menu) return;

    let existing = doc.getElementById('better-ocr-menu-item');
    if (existing) existing.remove();

    let menuItem;
    if (doc.createXULElement) {
        menuItem = doc.createXULElement('menuitem');
    } else {
        menuItem = doc.createElementNS('http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul', 'menuitem');
    }

	menuItem.setAttribute('id', 'better-ocr-menu-item');
	menuItem.setAttribute('label', 'Extract Text (Better OCR)');
    // REMOVED 'menuitem-iconic' to prevent blank display if icon fails
	// menuItem.setAttribute('class', 'menuitem-iconic'); 
    // menuItem.setAttribute('image', 'chrome://better-ocr/content/icon.png');

	menuItem.addEventListener('command', performOCR, false);
	
	menu.appendChild(menuItem);
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
        alert("Better OCR: No PDF attachments found.");
        return;
    }

    let pw = new Zotero.ProgressWindow();
    pw.changeHeadline("Better OCR");
    pw.show();
    let prog = new pw.ItemProgress("chrome://zotero/skin/tick.png", "Starting OCR...");
    prog.setProgress(10);

	try {
        let count = 0;
		for (let attachmentItem of pdfItems) {
            count++;
            prog.setText(`Processing ${count}/${pdfItems.length}: ${attachmentItem.getField('title').substring(0, 30)}...`);
            prog.setProgress((count / pdfItems.length) * 100);
            
			await processItem(attachmentItem);
		}
        prog.setText("OCR Complete.");
        pw.startCloseTimer(3000);
	} catch (e) {
		Zotero.logError(e);
        prog.setError();
        prog.setText("Error: " + e);
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

async function runBundledExecutable(pdfPath) {
	return new Promise(async (resolve, reject) => {
        let addons = await Zotero.getInstalledExtensions();
        let addon = addons.find(x => x.id == "better-ocr@lvigentini");
        if (!addon) return reject("Plugin ID 'better-ocr@lvigentini' not found. Installed: " + addons.map(a => a.id).join(", ")); 
        
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
