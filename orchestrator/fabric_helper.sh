#!/bin/bash

# Infrastructure Layer - Fabric Client Bridge (Bash)
#
# Script di supporto per l'interazione con la rete Hyperledger Fabric.
# Funge da Adapter tra l'applicazione Python e i binari del Peer (CLI).

# --- Configurazione Ambiente Fabric ---

# Imposta le variabili d'ambiente necessarie per interagire con Fabric
export FABRIC_SAMPLES_PATH=$HOME/fabric-samples  # Percorso base di Fabric samples
export PATH=$FABRIC_SAMPLES_PATH/bin:$PATH       # Aggiunge i binari Fabric al PATH
export FABRIC_CFG_PATH=$FABRIC_SAMPLES_PATH/config/  # Configurazione di Fabric
export CORE_PEER_TLS_ENABLED=true                # Abilita TLS per comunicazioni sicure
export CORE_PEER_LOCALMSPID="Org1MSP"            # ID dell'organizzazione (MSP)

# Percorso ai certificati dell'utente Admin di Org1 (per autenticazione)
export CORE_PEER_MSPCONFIGPATH=${FABRIC_SAMPLES_PATH}/test-network/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp

# Percorsi dei Certificati TLS necessari per verificare l'identità dei nodi
ORDERER_CA=${FABRIC_SAMPLES_PATH}/test-network/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
PEER1_TLS=${FABRIC_SAMPLES_PATH}/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
PEER2_TLS=${FABRIC_SAMPLES_PATH}/test-network/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt

# --- Lettura Argomenti e Configurazione ---

# Legge gli argomenti passati da Python: FUNCTION, ASSET_ID e argomenti variabili
FUNCTION=$1
ASSET_ID=$2
ARG3=$3
ARG4=$4
ARG5=$5
ARG6=$6
ARG7=$7

# Nome del chaincode deployato sulla rete Fabric
CC_NAME="basic"

# --- Esecuzione Comandi Fabric ---

# Operazione Create (Scrittura - Transazione)
# Crea un nuovo asset alimentare sulla blockchain
if [ "$FUNCTION" == "create" ]; then
    PRODUCT_TYPE=$ARG3
    QTY=$ARG4
    UNIT=$ARG5
    ORIGIN=$ARG6
    USER_ROLE=$ARG7

    echo "--- INVIO TRANSAZIONE A FABRIC: Creazione Asset $ASSET_ID ($PRODUCT_TYPE) da $USER_ROLE ---"
    
    # Invoca la funzione CreateAsset del chaincode
    peer chaincode invoke \
        -o localhost:7050 \
        --ordererTLSHostnameOverride orderer.example.com \
        --tls --cafile $ORDERER_CA \
        -C mychannel -n $CC_NAME \
        --peerAddresses localhost:7051 --tlsRootCertFiles $PEER1_TLS \
        --peerAddresses localhost:9051 --tlsRootCertFiles $PEER2_TLS \
        -c "{\"function\":\"CreateAsset\",\"Args\":[\"$ASSET_ID\", \"$PRODUCT_TYPE\", \"$QTY\", \"$UNIT\", \"$ORIGIN\", \"$USER_ROLE\"]}"

# Operazione Update (Scrittura - Transazione)
# Aggiorna lo stadio di un asset esistente sulla blockchain
elif [ "$FUNCTION" == "update" ]; then
    NEW_STAGE=$ARG3
    USER_ROLE=$ARG4

    echo "--- INVIO TRANSAZIONE A FABRIC: Aggiornamento Asset $ASSET_ID a '$NEW_STAGE' da $USER_ROLE ---"
    
    # Invoca la funzione UpdateStage del chaincode
    peer chaincode invoke \
        -o localhost:7050 \
        --ordererTLSHostnameOverride orderer.example.com \
        --tls --cafile $ORDERER_CA \
        -C mychannel -n $CC_NAME \
        --peerAddresses localhost:7051 --tlsRootCertFiles $PEER1_TLS \
        --peerAddresses localhost:9051 --tlsRootCertFiles $PEER2_TLS \
        -c "{\"function\":\"UpdateStage\",\"Args\":[\"$ASSET_ID\", \"$NEW_STAGE\", \"$USER_ROLE\"]}"

# Operazione Delete (Scrittura - Transazione)
# Elimina un asset esistente
elif [ "$FUNCTION" == "delete" ]; then
    USER_ROLE=$ARG3

    echo "--- INVIO TRANSAZIONE A FABRIC: Eliminazione Asset $ASSET_ID da $USER_ROLE ---"
    
    peer chaincode invoke \
        -o localhost:7050 \
        --ordererTLSHostnameOverride orderer.example.com \
        --tls --cafile $ORDERER_CA \
        -C mychannel -n $CC_NAME \
        --peerAddresses localhost:7051 --tlsRootCertFiles $PEER1_TLS \
        --peerAddresses localhost:9051 --tlsRootCertFiles $PEER2_TLS \
        -c "{\"function\":\"DeleteAsset\",\"Args\":[\"$ASSET_ID\", \"$USER_ROLE\"]}"

# Operazione Query (Lettura)
# Legge le informazioni di un asset (sola lettura, non modifica lo stato)
elif [ "$FUNCTION" == "query" ]; then
    echo "--- INTERROGAZIONE FABRIC: Lettura Asset $ASSET_ID ---"
    
    # Usa 'peer chaincode query' invece di 'invoke' perché è una sola lettura
    peer chaincode query \
        -C mychannel -n $CC_NAME \
        -c "{\"function\":\"ReadAsset\",\"Args\":[\"$ASSET_ID\"]}" \
        --tls --cafile $ORDERER_CA \
        --peerAddresses localhost:7051 --tlsRootCertFiles $PEER1_TLS
fi

# Il risultato viene restituito a Python tramite stdout/stderr e codice di ritorno