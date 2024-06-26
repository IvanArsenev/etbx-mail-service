export async function GetThemes(id: string): Promise<any> {
  const url = `http://etbx.ru:7070/get_themes_of_chat/${id}`;
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