export default interface UserAuth {
    username: string;
    password: string;
}

export interface UserObject {
    id: number;
    username: string;
    lastDate: string;
    lastTheme: string;
}

export const users: UserObject[] = [
    {
        id: 1,
        username: 'user@exapmle.com',
        lastDate: '01.01.2024',
        lastTheme: 'Last Theme'
    },
    {
        id: 2,
        username: 'user@exapmle.com',
        lastDate: '01.01.2024',
        lastTheme: 'Last Theme'
    },
    {
        id: 3,
        username: 'user@exapmle.com',
        lastDate: '01.01.2024',
        lastTheme: 'Last Theme'
    },
    {
        id: 4,
        username: 'user@exapmle.com',
        lastDate: '01.01.2024',
        lastTheme: 'Last Theme'
    },
]