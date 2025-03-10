from uuid import UUID, uuid4
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import Base, WalletsOrm
from .database import async_session, sync_engine
from .schemas import WalletResponse, OperationRequest, OperationType


Base.metadata.create_all(sync_engine)
app = FastAPI()

async def get_db():
    async with async_session() as session:
        yield session

@app.post('/api/v1/wallets/add', response_model=WalletResponse)
async def add_wallet(db: AsyncSession=Depends(get_db)) -> WalletResponse:
    wallet = WalletsOrm(uuid=uuid4(), balance=0)
    db.add(wallet)
    await db.commit()
    return WalletResponse(uuid=wallet.uuid, balance=wallet.balance)

@app.get('/api/v1/wallets/{wallet_uuid}', response_model=WalletResponse)
async def get_wallet(wallet_uuid: UUID, db: AsyncSession=Depends(get_db)) -> WalletResponse:
    async with db.begin():
        result = await db.execute(select(WalletsOrm).where(WalletsOrm.uuid == wallet_uuid))
        wallet = result.scalars().first()

        if not wallet:
            raise HTTPException(status_code=404, detail='Wallet not found')
        return WalletResponse(uuid=wallet.uuid, balance=wallet.balance)

@app.post('/api/v1/wallets/{wallet_uuid}/operation', response_model=WalletResponse)
async def operate_wallet(wallet_uuid: UUID, op: OperationRequest, db: AsyncSession=Depends(get_db)) -> WalletResponse:
    async with db.begin():
        result = await db.execute(
            select(WalletsOrm).where(WalletsOrm.uuid == wallet_uuid).with_for_update()
        )
        wallet = result.scalars().first()
        if not wallet:
            raise HTTPException(status_code=404, detail='Wallet not found')

        if op.operation_type == OperationType.DEPOSIT:
            wallet.balance += op.amount
        elif op.operation_type == OperationType.WITHDRAW:
            if wallet.balance < op.amount:
                raise HTTPException(status_code=400, detail='Insufficient funds')
            wallet.balance -= op.amount
        else:
            raise HTTPException(status_code=400, detail='Invalid operation type')

    return WalletResponse(uuid=wallet.uuid, balance=wallet.balance)