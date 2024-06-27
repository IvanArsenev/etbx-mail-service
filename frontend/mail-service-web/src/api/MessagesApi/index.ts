export async function GetMessages(userId:string, theme: string): Promise<any> {
  const url = `http://etbx.ru:7070/get_messages_by_theme/${userId}/${theme}`;
  try {
    const token = localStorage.getItem('mailServiceToken');
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
    });

    if (!response.ok) {
      return null;
    }
    const result = await response.json();
    
    return result;
  } catch {
    return null;
  }
}

export async function SendMessage(receiver:string, theme: string, body: string): Promise<any> {
  const url = `http://etbx.ru:7070/send`;
  const data = {
    receiver: receiver,
    body: body,
    theme: theme
  }
  try {
    const token = localStorage.getItem('mailServiceToken');
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      return null;
    }
    const result = await response.json();
    
    return result;
  } catch {
    return null;
  }
}