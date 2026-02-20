import React from 'react';

interface CategoryBadgeProps {
    category: string;
    href?: string;
    variant?: 'default' | 'light';
}

export function CategoryBadge({ category, href = '#', variant = 'default' }: CategoryBadgeProps) {
    const textColor = variant === 'light' ? 'text-gray-100' : 'text-gray-500';

    return (
        <a className={textColor} href={href}>
            <span className="inline-block h-3 border-l-2 border-red-600 mr-2"></span>
            {category}
        </a>
    );
}
