export default interface UserAuth {
    username: string;
    password: string;
}

export interface UserObject {
    id: number;
    Аватар: string | null;
    Дата_рождения: string;
    Имя: string;
    Номер_телефона: string | null;
    Пол: string;
    Почта: string;
    Фамилия: string;
}

export interface UserResponce {
    total_users: number;
    users: UserObject[];
}

// export const users: UserObject[] = [
//     {
//         id: 1,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 2,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 3,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 4,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 1,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 2,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 3,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 4,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 1,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 2,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 3,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 4,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 1,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 2,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 3,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 4,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 1,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 2,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 3,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
//     {
//         id: 4,
//         username: 'user@exapmle.com',
//         lastDate: '01.01.2024',
//         lastTheme: 'Last Theme'
//     },
// ]