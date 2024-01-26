(function () {

    if (window.wvds !== undefined) {
        return;
    }

    let receiver_url = "http://localhost:5000/gpt-plugin/wechat_video";

    function send_response_if_is_video(response) {
        if (response == undefined) {
            return;
        }

        if (response["err_msg"] != "H5ExtTransfer:ok") {
            return;
        }

        let value = JSON.parse(response["jsapi_resp"]["resp_json"]);

        if (value["object"] == undefined || value["object"]["object_desc"] == undefined || value["object"]["object_desc"]["media"].length == 0) {
            return;
        }

        fetch(receiver_url, {
            method: 'POST',
            mode: 'no-cors',
            body: JSON.stringify(value),
        }).then((resp) => {
            console.log(`video data for ${value["object"]["object_desc"]["description"]} sent`);
        });
    }

    function wrapper(name, origin) {
        console.log(`Injecting ${name}`);
        return function (...args) {
            const [cmdName, originalArgs, originalCallback] = args;
            console.log(`${name}("${cmdName}", ...) => args: `, originalArgs);
            if (args.length === 3) {
                args[2] = async function (...callbackArgs) {
                    if (callbackArgs.length === 1) {
                        send_response_if_is_video(callbackArgs[0]);
                    }
                    console.log(`${name}("${cmdName}", ...) => callback result (length: ${callbackArgs.length}):`);
                    console.log(callbackArgs.length === 1 ? callbackArgs[0] : callbackArgs);
                    return await originalCallback.apply(this, callbackArgs);
                };
            }

            return origin.apply(this, args);
        };
    }

    window.WeixinJSBridge.invoke = wrapper("WeixinJSBridge.invoke", window.WeixinJSBridge.invoke);
    window.wvds = true;
})();
