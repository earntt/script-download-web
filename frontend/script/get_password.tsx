export default async function GetPassword(mac:string){
    const response = await fetch(
        `https://script-download-backend.onrender.com/api/data?mac_address=${mac}`,
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );
    if(!response.ok){
        throw new Error("Failed to fetch data");
    }
    return await response.json();
}