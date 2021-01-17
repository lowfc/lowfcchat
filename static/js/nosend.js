/**
 * Создание объекта XMLHTTP
 */

function getXmlHttp() {
	var xmlhttp;
	try {
		xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
	} catch (e) {
	try {
		xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
	} catch (E) {
		xmlhttp = false;
	}
	}
	if (!xmlhttp && typeof XMLHttpRequest!='undefined') {
		xmlhttp = new XMLHttpRequest();
	}
	return xmlhttp;
}

/**
 * Получение форм изменения данных
 */


function sendMessage() {
	var xmlhttp = getXmlHttp();
	xmlhttp.open('POST', '/addmessage', true);
	xmlhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xmlhttp.send(encodeURIComponent('sender') + "&message=" + encodeURIComponent(document.getElementById('inputContent').value) + '&chatid=' + encodeURIComponent(document.getElementById('inputChatID').value));
	document.getElementById('inputContent').value = '';
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4) {
			if (xmlhttp.status == 200) {
				var box = document.getElementById('messageBox');
				box.innerHTML += xmlhttp.responseText;
			}
		}
	};
}

function killTheBox(id)
{
    const message_box = document.getElementById(id);
    message_box.remove();
}

function deleteMessage(id) {
	var xmlhttp = getXmlHttp();
	xmlhttp.open('POST', '/deletemessage', true);
	xmlhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xmlhttp.send(encodeURIComponent('messageBox') + "&messageid=" + encodeURIComponent(id));
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4) {
			if (xmlhttp.status == 200) {
				const message_box = document.getElementById(id);
                var box = document.getElementById(id);
				box.innerHTML = xmlhttp.responseText;
				setTimeout(killTheBox, 1000, id);
			}
		}
	};
}

function checkUpdate(chatid){
var xmlhttp = getXmlHttp();
	xmlhttp.open('POST', '/returnlastid', true);
	xmlhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xmlhttp.send("&chatid=" + encodeURIComponent(chatid));
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4) {
			if (xmlhttp.status == 200) {
				if (xmlhttp.responseText != document.getElementById('lastMessageID').value){
				    if (document.getElementById('lastMessageID').value!=''){
				        getAfterUpdate(chatid, document.getElementById('lastMessageID').value);
				    }
                    document.getElementById('lastMessageID').value = xmlhttp.responseText;
				}
				setTimeout(checkUpdate, 10000, chatid);
			}
		}
	};
}

function getAfterUpdate(chatid, lastMSGid){
    var xmlhttp = getXmlHttp();
	xmlhttp.open('POST', '/returnafterupdate', true);
	xmlhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	xmlhttp.send("&chatid=" + encodeURIComponent(chatid) + '&lastmessageid='+ encodeURIComponent(lastMSGid));
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4) {
			if (xmlhttp.status == 200) {
                var box = document.getElementById('messageBox');
				box.innerHTML += xmlhttp.responseText;
		}
	};
}
}