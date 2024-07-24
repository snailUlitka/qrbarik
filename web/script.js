async function postData(){
    let text = document.getElementById("qrGeneratorTextarea").value;

    if(text.length != 0){
        let textJSON = JSON.stringify({text: text});
        const response = await fetch('http://127.0.0.1:7845/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8'
            },
            body: textJSON
        })
    }
}