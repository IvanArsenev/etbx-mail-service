export async function UserMe(): Promise<any> {
  const url = 'http://etbx.ru:7070/users/me';
  try {
    const token = localStorage.getItem('mailServiceToken');

    if (!token) {
      console.error('No token found in localStorage');
      return null;
    }
  } catch {
    return null;
  }
  

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
  } catch (error) {
    return null;
  }
}

export async function Logout(): Promise<any> {
  const url = 'http://etbx.ru:7070/logout';
  const token = localStorage.getItem('mailServiceToken');

  if (!token) {
    console.error('No token found in localStorage');
    return null;
  }

  try {
    const response = await fetch(url, {
      method: 'POST',
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
  } catch (error) {
    return null;
  }
}

export async function UsersAll(): Promise<any> {
  const url = 'http://etbx.ru:7070/users?page=1&page_size=100000';
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

export async function GetAvatar(imageName: string): Promise<any> {
  const url = `http://etbx.ru:7070/avatars/${imageName}`;
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